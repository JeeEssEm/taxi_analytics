from django.http import Http404, HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from .models import TaxiOrder
from .models import TaxiDriver


class ClientActiveOrderView(View):
    @method_decorator(login_required)
    def get(self, request: HttpRequest):
        try:
            order = TaxiOrder.objects.get(user_id=request.user.id,
                                          status='ON_THE_WAY')
        except TaxiOrder.DoesNotExist:
            raise Http404('No active orders')
        context = {'order': order}
        return render(request, 'orders/active_order_client.html', context)


class DriverActiveOrderView(View):
    @method_decorator(login_required)
    def get(self, request: HttpRequest):
        try:
            driver = TaxiDriver.objects.get(user_id=request.user.id)
        except TaxiDriver.DoesNotExist:
            raise Http404('Driver does not exist')
        try:
            order = TaxiOrder.objects.get(driver_id=driver.id, 
                                          status='ON_THE_WAY')
        except TaxiOrder.DoesNotExist:
            raise Http404('Order does not exist')
        context = {'order': order}
        return render(request, 'orders/active_order_driver.html', context)


class ClientNewOrderView(View):
    @method_decorator(login_required)
    def get(self, request: HttpRequest):
        return render(request, 'orders/new_order_client.html')


class DriverNewOrderView(View):
    @method_decorator(login_required)
    def get(self, request: HttpRequest):
        try:
            TaxiDriver.objects.get(user_id=request.user.id)
        except TaxiDriver.DoesNotExist:
            raise Http404('Driver does not exist')
        return render(request, 'orders/new_order_driver.html')
