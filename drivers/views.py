from datetime import datetime, timezone
import json

from django.contrib.auth.views import LoginView
from django.http.response import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, View, UpdateView, CreateView, ListView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView

from orders.utils import get_status_info
from orders.serializers import OrderSerializer
from drivers.mixins import UserIsDriverOfOrderMixin, DriverInformationMixin
from drivers.utils import get_available_driver_actions
import drivers.forms as driver_forms
import users.models as users_models
import orders.models as order_models
import reviews.models as review_models
import users.forms as user_forms
import drivers.models as drivers_models
import cars.models as cars_models


class BecomeDriverView(LoginRequiredMixin, DriverInformationMixin, CreateView):
    template_name = "drivers/become.html"
    form_class = driver_forms.DriverForm
    model = cars_models.TaxiCar
    success_url = reverse_lazy("drivers:new_orders")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['car_form'] = driver_forms.CarForm(self.request.POST)
        else:
            context['car_form'] = driver_forms.CarForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.taxi:
            return redirect(reverse_lazy('drivers:new_orders'))
        return super().get(request, *args, **kwargs)


class ChangeDriverActivityView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.user.taxi.status == drivers_models.TaxiDriver.StatusChoices.INACTIVE:
            request.user.taxi.status = drivers_models.TaxiDriver.StatusChoices.WAITING
            request.user.taxi.save()
            return redirect(reverse_lazy('drivers:new_orders'))
        if request.user.taxi.status == drivers_models.TaxiDriver.StatusChoices.WORKING:
            return HttpResponse(status=403, message='You cannot change activity while working')
        request.user.taxi.status = drivers_models.TaxiDriver.StatusChoices.INACTIVE
        request.user.taxi.save()
        return redirect(reverse_lazy('drivers:new_orders'))


class UpdateDriverInformationView(LoginRequiredMixin, DriverInformationMixin, UpdateView):
    model = drivers_models.TaxiDriver
    form_class = driver_forms.DriverForm
    template_name = 'drivers/edit_information.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['car_form'] = driver_forms.CarForm(self.request.POST)
        else:
            context['car_form'] = driver_forms.CarForm(instance=self.object.car)
        return context

    def get_object(self, queryset=None):
        return self.request.user.taxi

    def get_success_url(self):
        return reverse_lazy('drivers:new_orders')


class OrdersListView(LoginRequiredMixin, View):
    template_name = "drivers/orders.html"
    context_object_name = "orders"
    refresh_interval = 15 * 1000  # 15 секунд

    def dispatch(self, request, *args, **kwargs):
        if not request.user.taxi:
            return redirect(reverse_lazy("drivers:become"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return order_models.TaxiOrder.objects.all()  # TODO: добавить сортировку по расстоянию и фильтрацию по статусу

    def get(self, request, *args, **kwargs):
        # если ajax, то возвращаем json
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            orders: list[order_models.TaxiOrder] = self.get_queryset()
            return JsonResponse(
                {
                    'orders': OrderSerializer.get_orders(request, orders),
                    'refresh_interval': self.refresh_interval,
                }
            )
        context = {
                'refresh_interval': self.refresh_interval // 1000,
            }
        active_order = order_models.TaxiOrder.objects.get_active_order_driver(self.request.user.id).first()
        if active_order:
            context['active_order'] = active_order
        return render(
            request, self.template_name, context
        )


class OrdersHistoryView(LoginRequiredMixin, ListView):
    template_name = "drivers/history.html"
    context_object_name = "orders"
    paginate_by = 5

    def get_queryset(self):
        return order_models.TaxiOrder.objects.get_completed_orders_by_driver(self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_order = order_models.TaxiOrder.objects.get_active_order_driver(self.request.user.id).first()
        unrated_orders_amount = order_models.TaxiOrder.objects.get_unrated_orders_by_driver(self.request.user.taxi).count()

        if active_order:
            context['active_order'] = active_order
            context['active_order_status'] = get_status_info(active_order.status)
        if unrated_orders_amount > 0:
            context['show_banner'] = True
            context['user_role'] = 'driver'
            context['pending_count'] = unrated_orders_amount
        return context


class OrderDetailView(LoginRequiredMixin, UserIsDriverOfOrderMixin,  DetailView):
    template_name = "drivers/order_driver_detail.html"
    context_object_name = "order"

    def get(self, request, *args, **kwargs):
        context = {
            "order": self.order,
            "status_info": get_status_info(self.order.status),
            "yandex_api_key": settings.YANDEX_MAPS_API_KEY,
            "pickup_coords": [self.order.pickup_coords.y, self.order.pickup_coords.x][::-1],
            "dropoff_coords": [self.order.dropoff_coords.y, self.order.dropoff_coords.x][::-1],
            "available_actions": json.dumps(get_available_driver_actions(self.order.status))
        }
        return render(request, self.template_name, context)


class OrderStatusUpdateView(LoginRequiredMixin, UserIsDriverOfOrderMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        status = data.get("status")
        correct_statuses = list(map(lambda c: c[0], order_models.TaxiOrder.StatusChoices.choices))
        if self.order.status in (
            order_models.TaxiOrder.StatusChoices.DONE,
            order_models.TaxiOrder.StatusChoices.CANCELLED
        ):
            return JsonResponse({
                "success": False,
                "message": "Order already completed"
            }, status=403)
        if status not in correct_statuses:
            return JsonResponse({
                "success": False,
                "message": f"Status incorrect. Valid statuses: {correct_statuses}"
            }, status=403)
        self.order.status = status
        response_data = {
            "success": True,
            "new_status": status,
            "old_status": self.order.status,
        }
        if status == order_models.TaxiOrder.StatusChoices.DONE:
            self.order.dropoff_datetime = datetime.now()
            # TODO: проверка на extra
            self.order.driver.status = drivers_models.TaxiDriver.StatusChoices.WAITING
            self.order.driver.save()
            response_data["redirect_url"] = reverse_lazy("reviews:review", kwargs={"pk": self.order.id})
        if status == order_models.TaxiOrder.StatusChoices.CANCELLED:
            self.order.driver.status = drivers_models.TaxiDriver.StatusChoices.WAITING
            self.order.driver.save()

        self.order.save()
        return JsonResponse(response_data)


class OrderStatusView(LoginRequiredMixin, UserIsDriverOfOrderMixin, View):
    def get(self, request, *args, **kwargs):
        status_info = get_status_info(self.order.status)
        available_actions = get_available_driver_actions(self.order.status)

        data = {
            'status': self.order.status,
            'status_display': status_info['display'],
            'status_color': status_info['color'],
            'status_icon': status_info['icon'],
            'status_description': status_info.get('description', ''),
            'available_actions': available_actions,
            'client_name': self.order.client.get_full_name(),
            'client_phone': self.order.client.phone,
        }

        return JsonResponse(data)


class TakeOrderView(LoginRequiredMixin, UserIsDriverOfOrderMixin, View):
    def post(self, request, *args, **kwargs):
        if order_models.TaxiOrder.objects.get_active_order_driver(self.request.user).exists():
            return HttpResponseBadRequest()
        driver: drivers_models.TaxiDriver = self.request.user.taxi
        self.order.driver = driver
        self.order.car = driver.car
        self.order.status = order_models.TaxiOrder.StatusChoices.WAITING_FOR_DRIVER
        self.order.save()
        driver.status = drivers_models.TaxiDriver.StatusChoices.WORKING
        driver.save()
        return redirect(reverse_lazy("drivers:order_detail", kwargs={"pk": self.order.id}))
