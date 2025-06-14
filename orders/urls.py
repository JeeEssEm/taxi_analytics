from django.urls import path

import orders.views as views

app_name = "orders"

urlpatterns = [
    path("create/", views.CreateOrderView.as_view(), name="create_order"),
    path("get_order_price/", views.CalculateOrderPriceView.as_view(), name="get_order_price"),
    path("<int:pk>/status/", views.OrderStatusView.as_view(), name="order_status"),
    path("<int:pk>/cancel/", views.CancelOrderView.as_view(), name="cancel"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="detail"),
]
