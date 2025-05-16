from django.urls import path

from app.views.views import CustomRedirectView
from auth.views.auth.auth import (
    SignupView, LoginView, LogoutView
)

app_name = "auth"


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
]
