from django.db import models


class TaxiCar(models.Model):
    plate_number = models.CharField(max_length=10, null=False)
    car_manufactire = models.CharField(max_length=100, null=False)
    car_model = models.CharField(max_length=100, null=False)
    car_color = models.CharField(max_length=100, null=False)
