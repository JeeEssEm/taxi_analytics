from django.db import models
from users.models import TaxiUser
from drivers.models import TaxiDriver
from cars.models import TaxiCar
from orders.models import TaxiOrder
from orders.utils import get_address_coords, get_order_summary
import randvalues
import random
import pytz
import datetime


def register_random_car():
    return TaxiCar.objects.create(
        plate_number=random.choice(randvalues.plates),
        car_manufacture=random.choice(randvalues.manufactureres),
        car_model=random.choice(randvalues.models),
        car_color=random.choice(randvalues.colors),
        year=1984
    )


def register_random_driver():
    car = register_random_car()
    return TaxiDriver.objects.create(
        car=car
    )


def register_random_user(is_driver=False):
    if is_driver:
        driver = register_random_driver()
    else:
        driver = None

    return TaxiUser.objects.create(
        email=random.choice(randvalues.emails),
        first_name=random.choice(randvalues.firstnames),
        middle_name=random.choice(randvalues.middlenames),
        last_name=random.choice(randvalues.lastnames),
        driver=driver
    )


def register_random_order():
    user = random.choice(TaxiUser.objects.filter(driver__isnull=True).all())
    driver = random.choice(TaxiDriver.objects.all())
    pickup_coords = random.choice(randvalues.coords)
    dropoff_coords = random.choice(
        [x for x in randvalues.coords if x != pickup_coords])

    def coords_to_string(coords: list[2]):
        return f"{coords[0]},{coords[1]}"
    order = get_order_summary(coords_to_string(
        pickup_coords), coords_to_string(dropoff_coords), 1)

    return TaxiOrder(
        driver=driver,
        car=driver.car,
        client=user,

        pickup_coords=pickup_coords,
        pickup_verbose=get_address_coords(coords_to_string(pickup_coords)),

        dropoff_coords=dropoff_coords,
        dropoff_verbose=get_address_coords(coords_to_string(dropoff_coords)),

        passenger_count=1,
        trip_distance_km=order['distance'],
        expected_duration=order['duration']
    )
