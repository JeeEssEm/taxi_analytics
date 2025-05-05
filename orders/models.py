from django.db import models
from django.contrib.gis.db import models
from drivers.models import TaxiDriver
from cars.models import TaxiCar
from users.models import TaxiUser
from reviews.models import TaxiReview

class TaxiOrder(models.Model):
    driver_id = models.ForeignKey(TaxiDriver, null=False)
    car_id = models.ForeignKey(TaxiCar, null=False)
    cliend_id = models.ForeignKey(TaxiUser, null=False)
    review_id = models.ForeignKey(TaxiReview)
    
    STATUSES = {'CANCELLED': 'Cancelled', 'ON_THE_WAY': 'On the way', 'DONE': 'done'}
    status = models.CharField(choices=STATUSES)
    
    pickup_datetime = models.DateTimeField()
    pickup_coords = models.GeometryField(geography=True)

    dropoff_datetime = models.DateTimeField()
    dropoff_coords = models.GeometryField(geography=True)

    passenger_count = models.SmallIntegerField()
    trip_distance_km = models.IntegerField()
    
    PAYMENTS = (
        (0, 'CARD'),
        (1, 'CASH')
    )
    payment_type = models.SmallIntegerField(choices=PAYMENTS)
    
    extra = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
