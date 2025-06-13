from django.urls import path

from drivers import views

app_name = "drivers"

urlpatterns = [
    path("become/", views.BecomeDriverView.as_view(), name="become"),
    path("change_activity_status/", views.ChangeDriverActivityView.as_view(), name="change_activity_status"),
]
