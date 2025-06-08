from django.urls import path

from drivers import views

app_name = "drivers"

urlpatterns = [
    path("become/", views.BecomeDriverView.as_view(), name="become"),
]
