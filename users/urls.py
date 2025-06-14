import django.contrib.auth.views as auth_views
from django.urls import path
from django.urls import reverse_lazy

from . import views

app_name = "users"

urlpatterns = [
    path(
        "login/",
        views.ModifiedLoginView.as_view(
            template_name="users/login.html",
            redirect_authenticated_user=True,
            success_url=reverse_lazy("orders:create_order"),
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            template_name="users/logout.html",
            next_page=reverse_lazy("home:index"),
        ),
        name="logout",
    ),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path(
        "activate_after_signup",
        views.ActivateAfterSignUpView.as_view(),
        name="activate_after_signup",
    ),
    path(
        "resend_activation_email/",
        views.ResendActivationEmailView.as_view(),
        name="resend_activation_email",
    ),
    path("activate/", views.ActivateUserView.as_view(), name="activate"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path(
        "profile/<int:pk>/",
        views.ProfileView.as_view(),
        name="profile"
    ),
    path(
        "profile/<int:pk>/edit/",
        views.EditProfileView.as_view(),
        name="edit_profile"
    )
]
