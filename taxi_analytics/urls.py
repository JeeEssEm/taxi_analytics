from django.contrib import admin
from django.urls import path, include

import users.urls
import orders.urls
import reviews.urls
import home.urls

urlpatterns = [
    path("", include(home.urls)),
    path("admin/", admin.site.urls),
    path("users/", include(users.urls)),
    path("orders/", include(orders.urls)),
    path("reviews/", include(reviews.urls)),
]
