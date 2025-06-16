from datetime import timedelta, datetime

from django.db.models import (
    Count, Sum, ExpressionWrapper, DurationField, F, Manager, Q, Avg, When, FloatField,
    Case, Value, Subquery, OuterRef
)


class OrderManager(Manager):
    """
    Вспомогательный класс для запросов к базе данных
    """
    def get_profile_summary(self, user_id: int):
        result = self.filter(
            client_id=user_id,
            status="DONE"  # Только завершенные поездки
        ).aggregate(
            total_count=Count('id'),
            total_distance=Sum('trip_distance_km'),
            total_duration=Sum(
                ExpressionWrapper(
                    F('dropoff_datetime') - F('pickup_datetime'),
                    output_field=DurationField()
                )
            )
        )
        return {
            'total_count': result['total_count'] or 0,
            'total_distance': round(result['total_distance'] or 0.0),
            'total_duration': round((result['total_duration'] or timedelta()).total_seconds() / 60)
        }

    def get_amount_of_pending_orders(self) -> int:
        return self.filter(
            status="PENDING"
        ).aggregate(
            total_count=Count('id')
        )['total_count'] or 0

    def _get_active_orders_qs(self):
        return (
            self
            .filter(~Q(status="DONE"))
            .filter(~Q(status="CANCELLED"))
        )

    def get_active_order(self, user_id: int):
        return (
            self._get_active_orders_qs()
            .filter(client_id=user_id)
        )

    def get_active_order_driver(self, user):
        return (
            self._get_active_orders_qs()
            .filter(driver__user=user)
        )

    def get_completed_orders(self, user_id: int):
        return (
            self
            .filter(client_id=user_id)
            .filter(Q(status="DONE") | Q(status="CANCELLED"))
            .order_by('-created_at')
        )

    def get_completed_orders_by_driver(self, user_id: int):
        return (
            self
            .filter(driver__user=user_id)
            .filter(Q(status="DONE") | Q(status="CANCELLED"))
            .order_by('-created_at')
        )

    def _get_unrated_orders(self):
        return (
            self
            .filter(
                status__in=["DONE", "CANCELLED"]
            )
            .select_related(
                "driver__user", "car", "client"
            )
            .prefetch_related("review")
            .order_by("-created_at")
        )

    def get_unrated_orders_by_driver(self, driver):
        return self._get_unrated_orders().filter(
            driver=driver,
            review__driver_mark=None
        )

    def get_unrated_orders_by_client(self, client):
        return self._get_unrated_orders().filter(
            client=client,
            review__client_mark=None,
        )

    def get_available_orders(self):
        from reviews.models import TaxiReview

        rating_subquery = (
            TaxiReview.objects
            .filter(
                order__client=OuterRef('client'),
                driver_mark__isnull=False
            )
            .values('order__client')
            .annotate(avg_rating=Avg('driver_mark'))
            .values('avg_rating')
        )

        return (
            self
            .filter(
                status='PENDING',
                driver__isnull=True,
                created_at__gte=datetime.now() - timedelta(hours=1)
            )
            .select_related('client')
            .annotate(
                client_rating=Subquery(rating_subquery, output_field=FloatField())
            )
            .order_by(
                '-client_rating',
                'created_at',
                'trip_distance_km'
            )
        )
