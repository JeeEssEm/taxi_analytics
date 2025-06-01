from datetime import datetime, timedelta, timezone

from django.http.request import HttpRequest
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from jwt import encode, decode


def generate_jwt_token(user_id: int) -> str:
    token = encode(
        {
            "user_id": user_id,
            "exp": (
                datetime.now(timezone.utc)
                + timedelta(days=settings.JWT_EXPIRATION_DELTA_DAYS)
            ),
        },
        algorithm=settings.JWT_ALGORITHM,
        key=settings.SECRET_KEY,
    )
    return token


def decode_jwt_token(token: str) -> dict:
    return decode(token, key=settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def send_activation_email(user_id: int, email: str, request: HttpRequest):
    token = generate_jwt_token(user_id)
    link = (
        request.build_absolute_uri(reverse_lazy("users:activate")) + f"?token={token}"
    )

    link = f"<a href=\"{link}\">ссылке</a>"
    send_mail(
        subject="Активация аккаунта",
        message=f"Для активации аккаунта перейдите по {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
