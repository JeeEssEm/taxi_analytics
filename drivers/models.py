import os
import uuid

from django.db import models

from drivers.managers import DriversManager
from users.models import TaxiUser
from cars.models import TaxiCar


def upload_licenses(instance, filename):
    """
    :returns: Путь к директории с водительскими лицензиями   
    """
    return TaxiDriver.get_file_path(instance, filename, "driver_licenses")


def upload_rc(instance, filename):
    """
    :returns: Путь к директории с регистрационными сертификатами
    """
    return TaxiDriver.get_file_path(instance, filename, "registration_certificates")


class TaxiDriver(models.Model):
    """
    Модель таблицы базы данных, репрезентирующая водителя сервиса
    """
    objects = DriversManager()

    car = models.OneToOneField(TaxiCar, null=False, on_delete=models.CASCADE)
    driver_license = models.FileField(
        upload_to=upload_licenses,
        null=False
    )
    registration_certificate = models.FileField(
        upload_to=upload_rc,
        null=False
    )

    class StatusChoices(models.TextChoices):
        WORKING = "WORKING"
        INACTIVE = "INACTIVE"
        WAITING = "WAITING"

    status = models.CharField(choices=StatusChoices.choices)

    @staticmethod
    def get_file_path(inst, filename, path):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join(f'{path}/', filename)
