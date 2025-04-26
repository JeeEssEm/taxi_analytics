from django.db import models
from django.contrib.auth.models import AbstractUser


class TaxiUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)

    first_name = models.CharField(max_length=150, blank=False)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=False)
