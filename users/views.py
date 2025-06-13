from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, View, UpdateView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

import jwt

import users.models as users_models
import orders.models as order_models
import reviews.models as review_models
import users.forms as user_forms
from users.utils import send_activation_email, decode_jwt_token


class SignUpView(FormView):
    template_name = "users/signup.html"
    model = users_models.TaxiUser
    success_url = reverse_lazy("users:activate_after_signup")
    form_class = user_forms.SignUpForm

    def form_valid(self, form):
        user = form.save()
        user.is_active = settings.DEFAULT_USER_ACTIVITY
        user.save()
        self.request.session["registration_email"] = user.email

        if not settings.DEFAULT_USER_ACTIVITY:
            send_activation_email(user.id, form.cleaned_data.get("email"), self.request)

        return super().form_valid(form)


class ModifiedLoginView(LoginView):
    authentication_form = user_forms.LoginForm


class ResendActivationEmailView(FormView):
    form_class = user_forms.ResendActivationEmailForm
    template_name = "users/resend_activation.html"
    success_url = reverse_lazy("users:resend_activation_email")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = users_models.TaxiUser.objects.get(email=email)
            if user.is_active:
                form.add_error("email", "Аккаунт уже активирован")
                return super().form_invalid(form)

        except users_models.TaxiUser.DoesNotExist:
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
            user = get_object_or_404(users_models.TaxiUser, id=user_id)
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


class ProfileView(LoginRequiredMixin, View):
    template_name = "users/profile.html"

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        trip_summary = order_models.TaxiOrder.objects.get_profile_summary(pk)
        rating = review_models.TaxiReview.objects.get_user_rating(pk)
        user = users_models.TaxiUser.objects.get(pk=pk)
        return render(request, self.template_name, {
            "current_user": user,
            "trip_summary": trip_summary,
            "rating": rating,
            "pk": pk
        })


class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = "users/edit_profile.html"
    form_class = user_forms.ProfileForm
    model = users_models.TaxiUser

    def get_success_url(self):
        return reverse_lazy("users:edit_profile", kwargs={"pk": self.request.user.id})

    def get_object(self, queryset=None):
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        if pk != request.user.id:
            return redirect(reverse_lazy("users:profile", kwargs={"pk": pk}))
        return super(EditProfileView, self).dispatch(request, *args, **kwargs)
