from logging import getLogger

import openrouteservice
from django.conf import settings

from drivers.models import TaxiDriver
from orders.exceptions import RouteCannotBeBuiltException
from orders.models import TaxiOrder

LOGGER = getLogger(__name__)


def get_route(coords_pickup: tuple[float, float], coords_dropoff: tuple[float, float]):
    coords = (coords_pickup, coords_dropoff)
    client = openrouteservice.Client(key=settings.OPENROUTESERIVICE_APIKEY)
    route = client.directions(
        coords, units='km', instructions='false', preference='fastest')
    LOGGER.info(f"Got route: {route}")
    return route


def get_route_summary(route):
    routes = route.get("routes")
    if not routes:
        LOGGER.error(f"Route does not has routes: {route}")
        raise RouteCannotBeBuiltException(f"Route does not has routes: {route}")
    return routes["summary"]


def _calculate_base_price(distance: float, clear_time: float):
    fuel = distance * settings.AVG_PETROL_CONSUMPTION_LITER_PER_KM * settings.AVG_PETROL_CONSUMPTION_LITER_PER_KM
    salary = clear_time * settings.DRIVER_RATE_PER_MIN
    return fuel + salary


def _calculate_real_price(distance: float, clear_time: float, orders: int, free_cars: int):
    base_price = _calculate_base_price(distance, clear_time)
    ratio = orders / (free_cars + 0.001)  # чтоб на 0 не делить
    multiplier = max(1, min(ratio, settings.MAX_SURGE_VALUE))
    return base_price * multiplier


def get_order_summary(order: TaxiOrder):
    orders = TaxiOrder.objects.get_amount_of_pending_orders()
    free_cars = TaxiDriver.objects.get_amount_of_free_drivers()
    route_summary = get_route_summary(
        get_route(
            coords_pickup=order.pickup_coords.coords,
            coords_dropoff=order.dropoff_coords.coords
        )
    )
    return {
        "price": _calculate_real_price(
            distance=route_summary.get("distance", 0),
            clear_time=route_summary.get("duration", 0),
            orders=orders,
            free_cars=free_cars,
        ),
        "duration": route_summary.get("duration", 0),
        "distance": route_summary.get("distance", 0),
    }
