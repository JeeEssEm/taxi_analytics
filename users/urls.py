import django.contrib.auth.views as auth_views
from django.urls import path
from django.urls import reverse_lazy

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='users/login.html',
            redirect_authenticated_user=True,
            success_url=reverse_lazy('home:index')
        ),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            template_name='home/index.html',
        ),
        name='logout'
    ),
    path(
        'signup/',
        views.SignUpView.as_view(),
        name='signup'
    ),
]
