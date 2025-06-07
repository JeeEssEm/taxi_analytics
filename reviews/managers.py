from django.db.models import Manager, Avg


class ReviewManager(Manager):
    def get_user_rating(self, user_id: int):
        return (self
        .filter(client_id=user_id)
        .aggregate(
            rating=Avg('driver_mark')
        ))['rating'] or 0
