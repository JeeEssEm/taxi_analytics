from django.urls import path

from reviews import views


urlpatterns = [
    path("orders/<int:pk>/", views.CreateReviewView.as_view(), name="review"),
]
