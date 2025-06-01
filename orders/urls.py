from django.urls import path

from .views import ClientActiveOrderView
from .views import ClientNewOrderView
from .views import DriverActiveOrderView
from .views import DriverNewOrderView

urlpatterns = [
    path("client/active", ClientActiveOrderView.as_view(), name="client_active"),
    path("driver/active", DriverActiveOrderView.as_view(), name="driver_active"),
    path("client/new", ClientNewOrderView.as_view(), name="client_new"),
    path("driver/new", DriverNewOrderView.as_view(), name="driver_new"),
]
