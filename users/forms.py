from django.contrib.auth.forms import UserCreationForm

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
