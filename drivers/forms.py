from django.forms import Form, EmailField, ModelForm

import drivers.models as driver_models
import cars.models as cars_models


class DriverForm(ModelForm):
    """
    Класс репрезентирующий форму водителя
    """
    class Meta:
        model = driver_models.TaxiDriver
        fields = (
            driver_models.TaxiDriver.driver_license.field.name,
            driver_models.TaxiDriver.registration_certificate.field.name,
        )


class CarForm(ModelForm):
    """
    Класс репрезентирующий форму автомобиля
    """
    class Meta:
        model = cars_models.TaxiCar
        fields = (
            cars_models.TaxiCar.plate_number.field.name,
            cars_models.TaxiCar.car_manufacture.field.name,
            cars_models.TaxiCar.car_color.field.name,
            cars_models.TaxiCar.car_model.field.name,
            cars_models.TaxiCar.year.field.name
        )
