from django.urls import path

from app.views.views import CustomRedirectView
from authentication.views.auth.auth import (
    SignupView, LoginView, LogoutView,
    CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView,
    CustomPasswordChangeView
)

app_name = "authentication"


urlpatterns = [
    path("accounts/signup",
         CustomRedirectView.as_view(url="/signup", permanent=True)),
    path("signup", SignupView.as_view(), name="signup"),
    path("accounts/login",
         CustomRedirectView.as_view(url="/login", permanent=True)),
    path("login", LoginView.as_view(), name="login"),
    path("accounts/logout",
         CustomRedirectView.as_view(url="/logout", permanent=True)),
    path("logout", LogoutView.as_view(), name="logout"),

    # Password reset URLs
    path("password-reset/", CustomPasswordResetView.as_view(),
         name="password_reset"),
    path("password-reset/done/", CustomPasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("reset/done/", CustomPasswordResetCompleteView.as_view(),
         name="password_reset_complete"),
    path("password-change/", CustomPasswordChangeView.as_view(),
         name="password_change"),
    path("password-change/done/", CustomPasswordChangeView.as_view(),
         name="password_change_done"),
]
