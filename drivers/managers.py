from django.db.models import Count, Sum, ExpressionWrapper, DurationField, F, Manager


class DriversManager(Manager):
    def get_amount_of_free_drivers(self) -> int:
        return self.filter(
            status="PENDING"
        ).aggregate(
            total_amount=Count('id')
        ).get("total_amount") or 0
