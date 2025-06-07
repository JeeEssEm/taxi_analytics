from django.db import models
from django.contrib.gis.db import models
from drivers.models import TaxiDriver
from cars.models import TaxiCar
from users.models import TaxiUser
from reviews.models import TaxiReview


class TaxiOrder(models.Model):
    driver = models.ForeignKey(TaxiDriver, null=False, on_delete=models.CASCADE)
    car = models.ForeignKey(TaxiCar, null=False, on_delete=models.CASCADE)
    client = models.ForeignKey(TaxiUser, null=False, on_delete=models.CASCADE)
    review = models.ForeignKey(TaxiReview, on_delete=models.CASCADE)

    STATUSES = {"CANCELLED": "Cancelled", "ON_THE_WAY": "On the way", "DONE": "done"}
    status = models.CharField(choices=STATUSES)

    pickup_datetime = models.DateTimeField()
    pickup_coords = models.GeometryField(geography=True)

    dropoff_datetime = models.DateTimeField()
    dropoff_coords = models.GeometryField(geography=True)

    passenger_count = models.SmallIntegerField()
    trip_distance_km = models.IntegerField()

    PAYMENTS = ((0, "CARD"), (1, "CASH"))
    payment_type = models.SmallIntegerField(choices=PAYMENTS)

    extra = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
