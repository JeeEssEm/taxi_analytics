from django.db import models
from users.models import TaxiUser
from drivers.models import TaxiDriver


class TaxiReview(models.Model):
    driver = models.ForeignKey(TaxiDriver, on_delete=models.CASCADE)
    user = models.ForeignKey(TaxiUser, on_delete=models.CASCADE)
    mark = models.SmallIntegerField()
    review_verbose = models.TextField()
