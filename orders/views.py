from datetime import datetime, timezone, timedelta
import json
from logging import getLogger

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.views.generic import DetailView, View, ListView
from django.urls import reverse_lazy
from django.conf import settings

from orders.exceptions import RouteCannotBeBuiltException
from orders.utils import (
    get_order_summary, get_address_coords, create_order_signature, get_status_info,
    add_driver_to_context
)
from orders.forms import CreateOrderForm
from orders.serializers import OrderSerializer
from orders.models import TaxiOrder, TaxiDriver, TaxiUser
from reviews.models import TaxiReview

LOGGER = getLogger(__name__)


class CalculateOrderPriceView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            pickup_coords = data.get('pickup_coords')
            dropoff_coords = data.get('dropoff_coords')
            passengers = int(data.get('passengers', 1))

            if not all([pickup_coords, dropoff_coords]):
                return JsonResponse(
                    {
                        'success': False,
                        'error': 'Не указаны координаты'
                    }, status=400
                )

            try:
                summary = get_order_summary(pickup_coords, dropoff_coords, passengers)

                order_signature = create_order_signature({
                    'pickup_coords': pickup_coords,
                    'dropoff_coords': dropoff_coords,
                    'passengers': passengers,
                    'price': float(summary.get('price', 0))
                })

                response_data = {
                    'success': True,
                    'price': float(summary.get('price', 0)),
                    'distance': summary.get('distance', 0),
                    'duration': summary.get('duration', 0),
                    'order_signature': order_signature,
                }

                return JsonResponse(response_data)

            except RouteCannotBeBuiltException:
                return JsonResponse(
                    {
                        'success': False,
                        'error': 'Невозможно построить маршрут для указанного расстояния'
                    }, status=400
                )

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Некорректные данные'
                }, status=400
            )
        except Exception as e:
            LOGGER.error(f"Price calculation error: {e}")
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Ошибка при расчете стоимости'
                }, status=500
            )


class CreateOrderView(LoginRequiredMixin, View):
    template_name = "orders/create_order.html"

    def dispatch(self, request, *args, **kwargs):
        active_order = TaxiOrder.objects.get_active_order(request.user.id).first()
        if active_order:
            return redirect(reverse_lazy('orders:detail', kwargs={'pk': active_order.id}))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(
            request, self.template_name, {
                'yandex_api_key': settings.YANDEX_MAPS_API_KEY,
                'form': CreateOrderForm(),
            }
        )

    def post(self, request, *args, **kwargs):
        data = request.POST
        LOGGER.info(f'Received create order data: {data}')
        try:
            # проверяем подпись
            sig = create_order_signature(
                {
                    'pickup_coords': data.get('pickup_coords'),
                    'dropoff_coords': data.get('dropoff_coords'),
                    'passengers': int(data.get('passenger_count', 1)),
                    'price': float(data.get('order_price', 0)),
                }
            )
            current_server_time_utc = datetime.now(timezone.utc)

            pickup_datetime = datetime.fromisoformat(data.get('pickup_datetime'))
            if data.get('time_type') == 'now':
                pickup_datetime = current_server_time_utc
            pickup_datetime = pickup_datetime.replace(second=(pickup_datetime.second + 5) % 60)

            if sig != data.get('order_signature'):
                LOGGER.error(f'Signature error. Expected: {sig}. Got: {data.get("order_signature")}')
                return render(request, "orders/data_corrupted.html")
            # if pickup_datetime < current_server_time_utc:
            #     LOGGER.error(f'pickup_datetime is older than now: {pickup_datetime} > {current_server_time_utc}')
            #     return render(
            #         request,
            #         "orders/data_corrupted.html",
            #         {"message": "pickup datetime older than now!"}
            #     )

            pickup_verbose = get_address_coords(data.get('pickup_coords'))
            dropoff_verbose = get_address_coords(data.get('dropoff_coords'))

            new_order = TaxiOrder.objects.create(
                driver=None,
                car=None,
                client=request.user,
                pickup_datetime=pickup_datetime,
                pickup_coords=Point(*(map(float, data.get('pickup_coords').split(','))), srid=4326),
                pickup_verbose=pickup_verbose,
                dropoff_datetime=None,
                dropoff_coords=Point(*(map(float, data.get('dropoff_coords').split(','))), srid=4326),
                dropoff_verbose=dropoff_verbose,
                passenger_count=int(data.get('passenger_count')),
                trip_distance_km=float(data.get('distance')),
                expected_duration=int(data.get('expected_duration')),
                total=data.get('order_price', 0),
                comment=data.get('comment', ''),
                payment_type=int(data.get('payment_type', TaxiOrder.PaymentChoices.CASH)),
                extra=0,
                status=TaxiOrder.StatusChoices.PENDING
            )
            return redirect(reverse_lazy('orders:detail', kwargs={'pk': new_order.id}))

        except Exception as e:
            LOGGER.error(f"Order creation error: {e}")
            return render(request, 'orders/data_corrupted.html')


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = "orders/order_client_detail.html"
    model = TaxiOrder
    context_object_name = "order"

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return TaxiOrder.objects.filter(pk=pk)

    def get(self, request, *args, **kwargs):
        order: TaxiOrder = self.get_queryset().first()
        if not order:
            return HttpResponse(status=404)
        if order.client == request.user:
            context = {
                'order': order,
                'pickup_coords': [order.pickup_coords.y, order.pickup_coords.x][::-1],
                'dropoff_coords': [order.dropoff_coords.y, order.dropoff_coords.x][::-1],
                'status_info': get_status_info(order.status),
                'can_cancel': order.status in (
                    TaxiOrder.StatusChoices.WAITING_FOR_DRIVER,
                    TaxiOrder.StatusChoices.PENDING,
                    TaxiOrder.StatusChoices.DRIVER_WAITING,
                ),
                'yandex_api_key': settings.YANDEX_MAPS_API_KEY,
                'has_driver': order.driver is not None,
                'has_car': order.car is not None,
            }
            if order.driver:
                add_driver_to_context(context, order, request)
            return render(
                request,
                self.template_name,
                context=context
            )
        if order.driver and order.driver.user == request.user:
            return redirect(reverse_lazy('drivers:order_detail', kwargs={'pk': order.id}))
        return HttpResponse(status=404)


class OrderStatusView(View):
    def get(self, request, pk):
        try:
            order = get_object_or_404(TaxiOrder, id=pk)

            if order.client != request.user and (order.driver and order.driver.user != request.user):
                return JsonResponse({'error': 'Access denied'}, status=403)
            status_info = get_status_info(order.status)
            data = {
                'status': order.status,
                'status_display': status_info['display'],
                'status_color': status_info['color'],
                'status_icon': status_info['icon'],
                'status_description': status_info['description'],
                'updated_at': order.created_at.isoformat(),
                'has_driver': order.driver is not None,
                'has_car': order.car is not None,
            }

            if order.driver is not None:
                add_driver_to_context(data, order, request)

            return JsonResponse(data)
        except Exception as e:
            LOGGER.exception(f"Error occurred during getting order status: {e}")
            return JsonResponse({'error': 'Something went wrong'}, status=500)


class CancelOrderView(View):
    def post(self, request, pk, *args, **kwargs):
        order: TaxiOrder = get_object_or_404(TaxiOrder, id=pk)
        if (request.user == order.client and order.status in (
                order.StatusChoices.PENDING,
                order.StatusChoices.WAITING_FOR_DRIVER
        )) or request.user == order.driver:
            order.status = order.StatusChoices.CANCELLED
            order.save()
            if order.driver:
                order.driver.status = TaxiDriver.StatusChoices.WAITING
                order.driver.save()
            return JsonResponse({'success': True, 'display': 'Заказ успешно отменен'})

        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)


class OrdersHistoryView(LoginRequiredMixin, ListView):
    template_name = 'orders/history.html'
    context_object_name = 'orders'
    paginate_by = 5

    def get_queryset(self):
        return TaxiOrder.objects.get_completed_orders(self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_order = TaxiOrder.objects.get_active_order(self.request.user).first()
        unrated_orders_amount = TaxiOrder.objects.get_unrated_orders_by_client(self.request.user).count()
        if active_order:
            context['active_order'] = active_order
            context['active_order_status'] = get_status_info(active_order.status)
        if unrated_orders_amount > 0:
            context['show_banner'] = True
            context['user_role'] = 'client'
            context['pending_count'] = unrated_orders_amount

        return context
