import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "NOT SECRET KEY")
DEFAULT_USER_ACTIVITY = os.environ.get("DEFAULT_USER_ACTIVITY", "true").lower() in {
    "y",
    "yes",
    "true",
    "1",
    "t",
}

DEBUG = os.environ.get("DEBUG", "true").lower() in {
    "y",
    "yes",
    "true",
    "1",
    "t",
}

JWT_EXPIRATION_DELTA_DAYS = os.environ.get("JWT_EXPIRATION_DELTA_DAYS", 3)
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "users.apps.UsersConfig",
    "orders.apps.OrdersConfig",
    "drivers.apps.DriversConfig",
    "cars.apps.CarsConfig",
    "home.apps.HomeConfig",
    "reviews.apps.ReviewsConfig",
    "django.contrib.gis",
    "sorl.thumbnail"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "users.auth_backend.EmailLoginAuth",
]

INTERNAL_IPS = os.environ.get("INTERNAL_IPS", "*").split(",")

ROOT_URLCONF = "taxi_analytics.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "taxi_analytics.wsgi.application"

GDAL_LIBRARY_PATH = "/usr/lib/x86_64-linux-gnu/libgdal.so"
GEOS_LIBRARY_PATH = "/usr/lib/x86_64-linux-gnu/libgeos_c.so"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("DB_NAME", default="myproject"),
        "USER": os.environ.get("DB_USER", default="postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", default="postgres"),
        "HOST": os.environ.get("DB_HOST", default="db"),
        "PORT": os.environ.get("DB_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTH_USER_MODEL = "users.TaxiUser"

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static_dev",
]
STATIC_ROOT = BASE_DIR / "static"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.yandex.ru")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 465))
    EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "true").lower() in {
        "y",
        "yes",
        "true",
        "1",
        "t",
    }

    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "<EMAIL>")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "<password>")

    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    SERVER_EMAIL = EMAIL_HOST_USER
    EMAIL_ADMIN = EMAIL_HOST_USER
