from datetime import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class TaxiCar(models.Model):
    plate_number = models.CharField(max_length=10, null=False)
    car_manufacture = models.CharField(max_length=100, null=False)
    car_model = models.CharField(max_length=100, null=False)
    car_color = models.CharField(max_length=100, null=False)
    year = models.IntegerField(null=False, validators=[
        MinValueValidator(1900), MaxValueValidator(datetime.now().year + 1)
    ])
