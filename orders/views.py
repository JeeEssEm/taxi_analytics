from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView, View
from django.urls import reverse_lazy

from orders.serializers import OrderSerializer
from orders.models import TaxiOrder, TaxiDriver, TaxiUser
from reviews.models import TaxiReview


class OrdersListView(LoginRequiredMixin, View): # TODO: ListView
    template_name = "orders/list.html"
    context_object_name = "orders"
    refresh_interval = 15 * 1000 # 15 секунд

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
            return JsonResponse({
                'orders': OrderSerializer.get_orders(request, orders),
                'refresh_interval': self.refresh_interval,
            })
        return render(request, self.template_name, {
            'refresh_interval': self.refresh_interval // 1000,
        })


class ClientActiveOrderView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        try:
            order = TaxiOrder.objects.get(user_id=request.user.id, status="ON_THE_WAY")
        except TaxiOrder.DoesNotExist:
            raise Http404("No active orders")
        context = {"order": order}
        return render(request, "orders/active_order_client.html", context)


class DriverActiveOrderView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        try:
            driver = TaxiDriver.objects.get(user_id=request.user.id)
        except TaxiDriver.DoesNotExist:
            raise Http404("Driver does not exist")
        try:
            order = TaxiOrder.objects.get(driver_id=driver.id, status="ON_THE_WAY")
        except TaxiOrder.DoesNotExist:
            raise Http404("Order does not exist")
        context = {"order": order}
        return render(request, "orders/active_order_driver.html", context)


class ClientNewOrderView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        return render(request, "orders/new_order_client.html")


class DriverNewOrderView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        try:
            TaxiDriver.objects.get(user_id=request.user.id)
        except TaxiDriver.DoesNotExist:
            raise Http404("Driver does not exist")
        return render(request, "orders/new_order_driver.html")
