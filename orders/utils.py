import hashlib
from logging import getLogger

from django.conf import settings
import requests
from drivers.models import TaxiDriver
from orders.exceptions import RouteCannotBeBuiltException
from orders.models import TaxiOrder

LOGGER = getLogger(__name__)


def get_route_summary(pickup_coords: str, dropoff_coords: str):
    pickup_lat, pickup_lng = map(float, pickup_coords.split(','))
    dropoff_lat, dropoff_lng = map(float, dropoff_coords.split(','))

    url = "https://graphhopper.com/api/1/route"

    params = {
        'point': [f"{pickup_lat},{pickup_lng}", f"{dropoff_lat},{dropoff_lng}"],
        'vehicle': 'car',
        'locale': 'ru',
        'calc_points': 'false',
        'debug': 'false',
        'elevation': 'false',
        'points_encoded': 'false',
        'type': 'json',
        'key': settings.GRAPHHOPPER_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            LOGGER.error(f"GraphHopper API error: {response.status_code} - {response.text}")
            raise Exception(f"GraphHopper API returned status {response.status_code}")

        data = response.json()
        if 'message' in data:
            LOGGER.error(f"GraphHopper API message: {data['message']}")
            raise Exception(f"GraphHopper error: {data['message']}")

        if not data.get('paths') or len(data['paths']) == 0:
            raise Exception("No routes found by GraphHopper")
        path = data['paths'][0]

        distance_meters = path.get('distance', 0)
        duration_ms = path.get('time', 0)

        distance_km = distance_meters / 1000
        duration_min = duration_ms / (1000 * 60)

        if distance_km <= 0 or duration_min <= 0:
            raise Exception("Invalid distance or duration from GraphHopper")

        LOGGER.info(f"GraphHopper success: distance={distance_km:.1f}km, duration={duration_min:.0f}min")

        return {
            'distance': round(distance_km, 1),
            'duration': round(duration_min),
        }

    except requests.exceptions.Timeout:
        LOGGER.error("GraphHopper API timeout")
        raise Exception("GraphHopper API timeout")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"GraphHopper API request error: {e}")
        raise Exception(f"GraphHopper API request failed: {e}")
    except Exception as e:
        LOGGER.error(f"GraphHopper calculation error: {e}")
        raise


def _calculate_base_price(distance: float, clear_time: float):
    fuel = distance * settings.AVG_PETROL_CONSUMPTION_LITER_PER_KM * settings.AVG_PETROL_PRICE_PER_LITER_RUB
    salary = clear_time * settings.DRIVER_RATE_PER_MIN
    return fuel + salary


def _calculate_real_price(distance: float, clear_time: float, orders: int, free_cars: int, passengers: int):
    base_price = _calculate_base_price(distance, clear_time)
    ratio = orders / (free_cars + 0.001)  # чтоб на 0 не делить
    multiplier = max(1, min(ratio, settings.MAX_SURGE_VALUE))
    passengers_factor = (1 + (passengers - 1) * 0.1)
    return round(base_price * multiplier * passengers_factor)


def get_order_summary(pickup_coords: str, dropoff_coords: str, passengers: int):
    orders = TaxiOrder.objects.get_amount_of_pending_orders()
    free_cars = TaxiDriver.objects.get_amount_of_free_drivers()
    route_summary = get_route_summary(
        pickup_coords,
        dropoff_coords
    )
    return {
        "price": _calculate_real_price(
            distance=route_summary.get("distance", 0),
            clear_time=route_summary.get("duration", 0),
            orders=orders,
            free_cars=free_cars,
            passengers=passengers
        ),
        "duration": route_summary.get("duration", 0),
        "distance": route_summary.get("distance", 0),
    }


def get_address_coords(coords_string: str):
    try:
        lat, lng = map(float, coords_string.split(','))

        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            'apikey': settings.YANDEX_MAPS_API_KEY,
            'geocode': f"{lng},{lat}",
            'format': 'json',
            'results': 1,
            'kind': 'house'
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            geo_objects = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])

            if geo_objects:
                geo_object = geo_objects[0]['GeoObject']
                address = geo_object.get('metaDataProperty', {}).get('GeocoderMetaData', {}).get('text', '')
                if address:
                    return address
        return f"Координаты: {lat:.6f}, {lng:.6f}"

    except Exception as e:
        LOGGER.error(f"Yandex geocoding failed: {e}")
        lat, lng = map(float, coords_string.split(','))
        return f"Координаты: {lat:.6f}, {lng:.6f}"


def create_order_signature(order_data):
    signature_string = f"{order_data['pickup_coords']}{order_data['dropoff_coords']}{order_data['passengers']}{order_data['price']}{settings.SECRET_KEY}"
    # return signature_string
    return hashlib.sha256(signature_string.encode()).hexdigest()[:16]
