from django.db import models
from users.models import TaxiUser
from cars.models import TaxiCar

class TaxiDriver(models.Model):
    car_id = models.ForeignKey(TaxiCar, null=False)
    user_id = models.ForeignKey(TaxiUser, null=False)

