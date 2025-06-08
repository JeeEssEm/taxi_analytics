from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, View, UpdateView, CreateView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

import drivers.forms as driver_forms
import users.models as users_models
import orders.models as order_models
import reviews.models as review_models
import users.forms as user_forms
import cars.models as cars_models


class BecomeDriverView(LoginRequiredMixin, CreateView):
    template_name = "drivers/become.html"
    form_class = driver_forms.DriverForm
    model = cars_models.TaxiCar
    success_url = reverse_lazy("orders:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['car_form'] = driver_forms.CarForm(self.request.POST)
        else:
            context['car_form'] = driver_forms.CarForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.taxi:
            return redirect(reverse_lazy())
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
