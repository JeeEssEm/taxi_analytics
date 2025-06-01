from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, View
from django.conf import settings

import jwt

from users import models
from users.forms import SignUpForm, ResendActivationEmailForm, LoginForm
from users.models import TaxiUser
from users.utils import send_activation_email, decode_jwt_token


class SignUpView(FormView):
    template_name = "users/signup.html"
    model = models.TaxiUser
    success_url = reverse_lazy("users:activate_after_signup")
    form_class = SignUpForm

    def form_valid(self, form):
        user = form.save()
        user.is_active = settings.DEFAULT_USER_ACTIVITY
        user.save()
        self.request.session["registration_email"] = user.email

        if not settings.DEFAULT_USER_ACTIVITY:
            send_activation_email(user.id, form.cleaned_data.get("email"), self.request)

        return super().form_valid(form)


class ModifiedLoginView(LoginView):
    authentication_form = LoginForm


class ResendActivationEmailView(FormView):
    form_class = ResendActivationEmailForm
    template_name = "users/resend_activation.html"
    success_url = reverse_lazy("users:resend_activation_email")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = models.TaxiUser.objects.get(email=email)
            if user.is_active:
                form.add_error("email", "Аккаунт уже активирован")
                return super().form_invalid(form)

        except TaxiUser.DoesNotExist:
            form.add_error("email", False)
            return super().form_invalid(form)
        send_activation_email(user.id, form.cleaned_data.get("email"), self.request)
        messages.success(
            self.request, "Письмо с кодом активации отправлено на вашу почту"
        )
        return super().form_valid(form)


class ActivateUserView(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        try:
            user_id = decode_jwt_token(token).get("user_id")
            user = get_object_or_404(TaxiUser, id=user_id)
            if user.is_active:
                return render(request, "users/failed_activation.html")
            user.is_active = True
            user.save()
            return render(request, "users/successful_activation.html")
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return render(request, "users/failed_activation.html")


class ActivateAfterSignUpView(View):
    template_name = "users/activation_after_signup.html"

    def get(self, request, *args, **kwargs):
        if settings.DEFAULT_USER_ACTIVITY:
            return redirect(reverse_lazy("users:login"))
        email = request.session.get("email", "вашу почту")
        return render(request, self.template_name, {"email": email})
