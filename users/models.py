from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from cars.models import TaxiCar


class TaxiUser(AbstractUser):
    """
    Модель базы данных, репрезентирующая абстрактного пользователя
    """
    email = models.EmailField(unique=True, blank=False)

    first_name = models.CharField(max_length=150, blank=False)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=False)

    image = models.ImageField(blank=True, null=True, upload_to="users_images/")

    phone = models.CharField(max_length=18, blank=True, validators=[
        RegexValidator(
            regex="\+[1-9]\d{1,4}[\s\-\(\)]?[\d\s\-\(\)]{4,14}",
            message="Номер телефона не соответствует заданному формату")
    ])
    taxi = models.OneToOneField("drivers.TaxiDriver", on_delete=models.CASCADE, related_name="user", null=True)

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}  {self.middle_name}"
