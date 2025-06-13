from datetime import timedelta

from django.db.models import Count, Sum, ExpressionWrapper, DurationField, F, Manager


class OrderManager(Manager):
    def get_profile_summary(self, user_id: int):
        result = self.filter(
            client_id=user_id,
            dropoff_datetime__isnull=False  # Только завершенные поездки
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
            'total_distance': result['total_distance'] or 0.0,
            'total_duration': (result['total_duration'] or timedelta()).total_seconds() / 60 / 60
        }

    def get_amount_of_pending_orders(self) -> int:
        return self.filter(
            status="PENDING"
        ).aggregate(
            total_count=Count('id')
        )['total_count'] or 0
