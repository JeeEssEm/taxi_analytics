from django.contrib.auth.views import LoginView
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, View, UpdateView, CreateView, ListView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from orders.utils import get_status_info
from orders.serializers import OrderSerializer
import drivers.forms as driver_forms
import users.models as users_models
import orders.models as order_models
import reviews.models as review_models
import users.forms as user_forms
import drivers.models as drivers_models
import cars.models as cars_models


class BecomeDriverView(LoginRequiredMixin, CreateView):
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

    def form_valid(self, form):
        context = self.get_context_data()
        car_form = context['car_form']
        if car_form.is_valid():
            car = car_form.save()
            self.object = form.save(commit=False)
            self.object.car = car
            self.object = form.save()

            self.request.user.taxi = self.object
            self.request.user.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))


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


class UpdateDriverInformationView(LoginRequiredMixin, UpdateView):
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

    def form_valid(self, form):
        context = self.get_context_data()
        car_form = context['car_form']
        if car_form.is_valid():
            car = car_form.save()
            self.object = form.save(commit=False)
            self.object.car = car
            self.object = form.save()

            self.request.user.taxi = self.object
            self.request.user.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))


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
        return render(
            request, self.template_name, {
                'refresh_interval': self.refresh_interval // 1000,
            }
        )


class OrdersHistoryView(LoginRequiredMixin, ListView):
    template_name = "drivers/history.html"
    context_object_name = "orders"
    paginate_by = 1

    def get_queryset(self):
        return order_models.TaxiOrder.objects.get_completed_orders_by_driver(self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_order = order_models.TaxiOrder.objects.get_active_order_driver(self.request.user.id).first()
        if active_order:
            context['active_order'] = active_order
            context['active_order_status'] = get_status_info(active_order.status)
        return context
