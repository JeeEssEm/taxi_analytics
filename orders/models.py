from django.db import models
from django.contrib.gis.db.models import GeometryField

from drivers.models import TaxiDriver
from cars.models import TaxiCar
from orders.managers import OrderManager
from users.models import TaxiUser


class TaxiOrder(models.Model):
    objects = OrderManager()

    driver = models.OneToOneField(TaxiDriver, null=True, on_delete=models.CASCADE)
    car = models.OneToOneField(TaxiCar, null=True, on_delete=models.CASCADE)
    client = models.OneToOneField(TaxiUser, null=False, on_delete=models.CASCADE)

    class StatusChoices(models.TextChoices):
        CANCELLED = "CANCELLED" # "Отменен"
        PENDING = "PENDING" # "Поиск водителя"
        WAITING_FOR_DRIVER = "WAITING_FOR_DRIVER" # "Водитель в пути"
        DONE = "DONE" # "Завершен"
        ON_THE_WAY = "ON_THE_WAY" # "В пути"
        DRIVER_WAITING = "DRIVER_WAITING" # "Водитель на месте"

    class PaymentChoices(models.IntegerChoices):
        CARD = 0
        CASH = 1

    status = models.CharField(choices=StatusChoices.choices, default=StatusChoices.PENDING)

    pickup_datetime = models.DateTimeField(null=True, blank=True)
    pickup_coords = GeometryField(geography=True)
    pickup_verbose = models.CharField()

    dropoff_datetime = models.DateTimeField(null=True, blank=True)
    dropoff_coords = GeometryField(geography=True)
    dropoff_verbose = models.CharField()

    passenger_count = models.SmallIntegerField()
    trip_distance_km = models.FloatField()
    expected_duration = models.FloatField()

    payment_type = models.SmallIntegerField(choices=PaymentChoices)

    extra = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(max_length=2000, blank=True, null=True)
