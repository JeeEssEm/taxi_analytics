from django.urls import path

from drivers import views

app_name = "drivers"

urlpatterns = [
    path("become/", views.BecomeDriverView.as_view(), name="become"),
    path("change_activity_status/", views.ChangeDriverActivityView.as_view(), name="change_activity_status"),
    path("edit/", views.UpdateDriverInformationView.as_view(), name="edit_driver"),
    path("orders/<int:pk>/status/", views.OrderStatusView.as_view(), name="order_status"),
    path("orders/<int:pk>/update_status/", views.OrderStatusUpdateView.as_view(), name="orders_update_status"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("orders/", views.OrdersListView.as_view(), name="new_orders"),
    path("history/", views.OrdersHistoryView.as_view(), name="history"),
]
