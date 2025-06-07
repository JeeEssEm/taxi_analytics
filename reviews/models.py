from typing import TYPE_CHECKING

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import TaxiUser
from drivers.models import TaxiDriver


class TaxiReview(models.Model):
    driver = models.ForeignKey(TaxiDriver, on_delete=models.CASCADE)
    user = models.ForeignKey(TaxiUser, on_delete=models.CASCADE)
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
    user_mark = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    user_review = models.TextField(blank=True, max_length=5000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
