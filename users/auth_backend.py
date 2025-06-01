from django.contrib.auth.backends import ModelBackend
from users.models import TaxiUser


class EmailLoginAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if "@" in username:
            kwargs = {"email": username}
        else:
            kwargs = {"username": username}

        try:
            user = TaxiUser.objects.get(**kwargs)
            if user.check_password(password):
                return user
            else:
                return None

        except TaxiUser.DoesNotExist:
            return None
