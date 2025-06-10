from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    ValidationError,
    authenticate,
)
from django.forms import Form, EmailField, ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe

from users import models


class SignUpForm(UserCreationForm):
    class Meta:
        model = models.TaxiUser
        fields = (
            models.TaxiUser.email.field.name,
            models.TaxiUser.username.field.name,
            models.TaxiUser.first_name.field.name,
            models.TaxiUser.middle_name.field.name,
            models.TaxiUser.last_name.field.name,
        )


class ResendActivationEmailForm(Form):
    email = EmailField(required=True)


class LoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            url = reverse("users:resend_activation_email")
            raise ValidationError(
                mark_safe(
                    "Этот аккаунт не активирован. Проверьте почту и активируйте аккаунт или перейдите по "
                    f"<a href='{url}' class='text-blue underline'>ссылке</a> для повторной активации"
                ),
                code="inactive",
            )

    def clean(self):
        username = self.cleaned_data.get(self.username_field.name)
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )

            if self.user_cache is None:
                user_for_status_check = None
                try:
                    if "@" in username:
                        user_for_status_check = models.TaxiUser.objects.get(
                            email=username
                        )
                    else:
                        user_for_status_check = models.TaxiUser.objects.get(
                            username=username
                        )
                except models.TaxiUser.DoesNotExist:
                    pass

                if (
                    user_for_status_check is not None
                    and not user_for_status_check.is_active
                ):
                    self.confirm_login_allowed(user_for_status_check)
                raise self.get_invalid_login_error()

            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class ProfileForm(ModelForm):
    class Meta:
        model = models.TaxiUser
        fields = (
            models.TaxiUser.email.field.name,
            models.TaxiUser.first_name.field.name,
            models.TaxiUser.middle_name.field.name,
            models.TaxiUser.last_name.field.name,
            models.TaxiUser.image.field.name,
            models.TaxiUser.phone.field.name
        )
