from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from reviews import managers
from users.models import TaxiUser
from drivers.models import TaxiDriver


class TaxiReview(models.Model):
    objects = managers.ReviewManager()
    driver = models.ForeignKey(TaxiDriver, on_delete=models.CASCADE)
    client = models.ForeignKey(TaxiUser, on_delete=models.CASCADE)
    order = models.OneToOneField(
        'orders.TaxiOrder',
        on_delete=models.CASCADE,
        related_name='review',
        null=True
    )
    driver_mark = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    driver_review = models.TextField(blank=True, max_length=5000)
    client_mark = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    client_review = models.TextField(blank=True, max_length=5000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
