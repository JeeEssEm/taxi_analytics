import hmac
import hashlib
import json
from logging import getLogger

from django.conf import settings
import requests

from drivers.models import TaxiDriver
from orders.exceptions import RouteCannotBeBuiltException
from orders.models import TaxiOrder
from orders.serializers import OrderSerializer

LOGGER = getLogger(__name__)


def get_route_summary(pickup_coords: str, dropoff_coords: str):
    """
    :returns: расчетные дистанцию поездки (в км) и продолжительность (в мин)
    """
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
    """
    :returns: расчетные дистанцию (в км), продолжительность (в мин) и цену (в рублях)
    """
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
    """
    :param coords_string: строка формата "<широта>,<долгота>"
    :returns: адрес соответствующий данной координате
    """
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
    """
    :returns: уникальная подпись заказа
    """
    normalized_data = {
        'pickup_coords': order_data['pickup_coords'],
        'dropoff_coords': order_data['dropoff_coords'],
        'passengers': int(order_data['passengers']),
        'price': float(order_data['price']),
    }

    data_string = json.dumps(normalized_data, sort_keys=True, ensure_ascii=False)

    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        msg=data_string.encode(),
        digestmod=hashlib.sha256
    )
    return signature.hexdigest()


def get_status_info(status):
    status_map = {
        TaxiOrder.StatusChoices.PENDING: {
            'display': 'Поиск водителя',
            'color': 'yellow',
            'icon': '⏳',
            'description': 'Ищем для вас водителя. Пожалуйста, подождите.'
        },
        TaxiOrder.StatusChoices.WAITING_FOR_DRIVER: {
            'display': 'Водитель в пути',
            'color': 'blue',
            'icon': '🚗',
            'description': 'Водитель принял заказ и едет к месту подачи'
        },
        TaxiOrder.StatusChoices.DRIVER_WAITING: {
            'display': 'Водитель на месте',
            'color': 'purple',
            'icon': '📍',
            'description': 'Водитель прибыл и ждет вас на месте подачи'
        },
        TaxiOrder.StatusChoices.ON_THE_WAY: {
            'display': 'В пути',
            'color': 'indigo',
            'icon': '🛣️',
            'description': 'Поездка началась, вы едете к месту назначения'
        },
        TaxiOrder.StatusChoices.DONE: {
            'display': 'Завершен',
            'color': 'green',
            'icon': '🏁',
            'description': 'Поездка успешно завершена'
        },
        TaxiOrder.StatusChoices.CANCELLED: {
            'display': 'Отменен',
            'color': 'red',
            'icon': '❌',
            'description': 'Заказ был отменен'
        }
    }
    return status_map.get(status, {
        'display': 'Неизвестно',
        'color': 'gray',
        'icon': '❓',
        'description': 'Статус неизвестен'
    })


def add_driver_to_context(context: dict, order: TaxiOrder, request):
    driver_data = {
        'name': order.driver.user.get_full_name(),
        'phone': order.driver.user.phone or None,
        'image_url': OrderSerializer.get_user_image(order.driver.user, request),
    }
    if order.car is not None:
        driver_data.update(
            {
                'car_model': f"{order.car.car_manufacture} {order.car.car_model}",
                'car_number': order.car.plate_number,
                'car_color': order.car.car_color,
                'car_year': order.car.year,
            }
        )
    context['driver'] = driver_data
