from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, View
from django.conf import settings

from users import models
from users.forms import SignUpForm


class SignUpView(FormView):
    template_name = 'users/signup.html'
    model = models.TaxiUser
    success_url = reverse_lazy('users:login')
    form_class = SignUpForm

    def form_valid(self, form):
        user = form.save()
        user.is_active = settings.DEFAULT_USER_ACTIVITY
        user.save()
        if not settings.DEFAULT_USER_ACTIVITY:
            ... # TODO: send email

        return super().form_valid(form)
