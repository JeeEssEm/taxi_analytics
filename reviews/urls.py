from django.urls import path

from reviews import views

app_name = 'reviews'

urlpatterns = [
    path("orders/<int:pk>/", views.CreateReviewView.as_view(), name="review"),
    path("driver/pending_reviews/", views.DriverPendingReviewsView.as_view(), name="driver_pending_reviews"),
    path("client/pending_reviews/", views.ClientPendingReviewsView.as_view(), name="client_pending_reviews"),
]
