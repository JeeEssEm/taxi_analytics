from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.conf.urls.static import static

import users.urls
import orders.urls
import reviews.urls
import home.urls
import drivers.urls
from taxi_analytics import settings

urlpatterns = [
    path("", include(home.urls)),
    path("admin/", admin.site.urls),
    path("users/", include(users.urls)),
    path("orders/", include(orders.urls)),
    path("reviews/", include(reviews.urls)),
    path("drivers/", include(drivers.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

    if hasattr(settings, 'MEDIA_ROOT'):
        urlpatterns += static(
            settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT,
        )
    else:
        urlpatterns += staticfiles_urlpatterns()
