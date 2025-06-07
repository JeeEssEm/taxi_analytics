from django.db import models
from users.models import TaxiUser
from cars.models import TaxiCar


class TaxiDriver(models.Model):
    car = models.ForeignKey(TaxiCar, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(TaxiUser, null=False, on_delete=models.CASCADE)
