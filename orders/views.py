import json
from logging import getLogger

from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView, View
from django.urls import reverse_lazy
from django.conf import settings

from orders.exceptions import RouteCannotBeBuiltException
from orders.utils import get_order_summary, get_address_coords, create_order_signature
from orders.forms import CreateOrderForm
from orders.serializers import OrderSerializer
from orders.models import TaxiOrder, TaxiDriver, TaxiUser
from reviews.models import TaxiReview

LOGGER = getLogger(__name__)


class OrdersListView(LoginRequiredMixin, View):  # TODO: ListView
    template_name = "orders/list.html"
    context_object_name = "orders"
    refresh_interval = 15 * 1000  # 15 секунд

    def dispatch(self, request, *args, **kwargs):
        if not request.user.taxi:
            return redirect(reverse_lazy("drivers:become"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return TaxiOrder.objects.all()  # TODO: добавить сортировку по расстоянию и фильтрацию по статусу

    def get(self, request, *args, **kwargs):
        # если ajax, то возвращаем json
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            orders: list[TaxiOrder] = self.get_queryset()
            return JsonResponse(
                {
                    'orders': OrderSerializer.get_orders(request, orders),
                    'refresh_interval': self.refresh_interval,
                }
            )
        return render(
            request, self.template_name, {
                'refresh_interval': self.refresh_interval // 1000,
            }
        )


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

                order_data = {
                    'pickup_coords': pickup_coords,
                    'dropoff_coords': dropoff_coords,
                    'passengers': passengers,
                    'price': float(summary.get('price', 0)),
                    'distance': summary.get('distance', 0),
                    'duration': summary.get('duration', 0)
                }

                order_signature = create_order_signature(order_data)

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

    def get(self, request, *args, **kwargs):
        return render(
            request, self.template_name, {
                'yandex_api_key': settings.YANDEX_MAPS_API_KEY
            }
        )

    def post(self, request, *args, **kwargs):
        pass
