import django.contrib.auth.views as auth_views
from django.urls import path

app_name = 'users'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='logout'
    ),
    path(
        'signup/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='signup'
    ),

]
