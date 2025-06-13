import openrouteservice
from models import TaxiOrder

OPENROUTESERIVICE_APIKEY = '5b3ce3597851110001cf62483eef4dfb3c0040bda5c7c27abdb74514'
AVG_PETROL_PRICE_PER_LITER_RUB = 60
AVG_PETROL_CONSUMP_LITER_PER_KM = 0.1
OVERPRICE_PERCENT = 0.7


def getRoute(order=TaxiOrder):
    coords_pickup = order.pickup_coords.coords
    coords_dropoff = order.dropoff_coords.coords
    coords = (coords_pickup, coords_dropoff)
    client = openrouteservice.Client(key=OPENROUTESERIVICE_APIKEY)
    route = client.directions(
        coords, units='km', instructions='false', preference='fastest')
    print(route)
    return route


def calcPrice_RUB(route):
    distance_km = route['routes']['summary']['distance']
    return distance_km * AVG_PETROL_PRICE_PER_LITER_RUB * AVG_PETROL_CONSUMP_LITER_PER_KM * (1 + OVERPRICE_PERCENT)
