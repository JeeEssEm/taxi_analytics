from django.db import models
from users.models import TaxiUser
from drivers.models import TaxiDriver

class TaxiReview(models.Model):
    driver_id = models.ForeignKey(TaxiDriver)
    user_id = models.ForeignKey(TaxiUser)
    mark = models.SmallIntegerField()
    review_verbose = models.TextField()
