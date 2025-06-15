from django.db.models import Manager, Avg


class ReviewManager(Manager):
    def get_user_rating(self, user):
        return (self
        .filter(order__client_id=user)
        .aggregate(
            rating=Avg('driver_mark')
        ))['rating'] or 0

    def get_driver_rating(self, driver):
        return (self
        .filter(order__driver=driver)
        .aggregate(
            rating=Avg('client_mark')
        ))['rating'] or 0
