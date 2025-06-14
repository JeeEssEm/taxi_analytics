from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("promo/", views.IndexView.as_view(), name="index"),
    path("", views.RedirectView.as_view(), name="redirect"),
]
