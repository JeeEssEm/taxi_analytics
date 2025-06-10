from django.db import models
from django.contrib.gis.db import models

from drivers.models import TaxiDriver
from cars.models import TaxiCar
from orders.managers import OrderManager
from users.models import TaxiUser


class TaxiOrder(models.Model):
    objects = OrderManager()

    driver = models.OneToOneField(TaxiDriver, null=False, on_delete=models.CASCADE)
    car = models.OneToOneField(TaxiCar, null=False, on_delete=models.CASCADE)
    client = models.OneToOneField(TaxiUser, null=False, on_delete=models.CASCADE)

    class StatusChoices(models.TextChoices):
        CANCELLED = "CANCELLED" # "Отменен"
        PENDING = "PENDING" # "Поиск водителя"
        WAITING_FOR_DRIVER = "WAITING_FOR_DRIVER" # "Водитель в пути"
        DONE = "DONE" # "Завершен"
        ON_THE_WAY = "ON_THE_WAY" # "В пути"
        DRIVER_WAITING = "DRIVER_WAITING" # "Водитель на месте"

    status = models.CharField(choices=StatusChoices.choices)

    pickup_datetime = models.DateTimeField(null=True, blank=True)
    pickup_coords = models.GeometryField(geography=True)

    dropoff_datetime = models.DateTimeField(null=True, blank=True)
    dropoff_coords = models.GeometryField(geography=True)

    passenger_count = models.SmallIntegerField()
    trip_distance_km = models.IntegerField()

    PAYMENTS = ((0, "CARD"), (1, "CASH"))
    payment_type = models.SmallIntegerField(choices=PAYMENTS)

    extra = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
