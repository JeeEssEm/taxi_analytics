from django.db import models
from users.models import TaxiUser
from drivers.models import TaxiDriver


class TaxiReview(models.Model):
    driver_id = models.ForeignKey(TaxiDriver, on_delete=models.CASCADE)
    user_id = models.ForeignKey(TaxiUser, on_delete=models.CASCADE)
    mark = models.SmallIntegerField()
    review_verbose = models.TextField()
