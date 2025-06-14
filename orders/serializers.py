from typing import Iterable

from sorl.thumbnail import get_thumbnail

from reviews.models import TaxiReview
from orders.models import TaxiOrder


class OrderSerializer:
    @staticmethod
    def get_user_image(user, request):
        if user.image:
            thumb = get_thumbnail(user.image, '40x40', crop='center')
            return request.build_absolute_uri(thumb.url)
        return None

    @staticmethod
    def get_orders(request, orders: Iterable[TaxiOrder]):
        return [
            {
                'id': order.id,
                'start_address': order.pickup_verbose,
                'end_address': order.dropoff_verbose,
                'price': order.total,
                'distance': order.trip_distance_km,
                'created_at': order.created_at.strftime("%H:%M %d.%m.%Y"),
                'passenger': {
                    'name': order.client.get_full_name(),
                    'rating': TaxiReview.objects.get_user_rating(order.client.id),
                    'image': OrderSerializer.get_user_image(order.client, request)
                },
            }
            for order in orders
        ]
