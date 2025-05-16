from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.views.generic.base import TemplateView

from django.contrib.auth.views import (
    PasswordChangeView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

from auth.forms.auth import LoginForm, SignupForm
from auth.views.auth.base import BaseAuthentication
from app.views.helpers.helpers import is_ajax


class SignupView(BaseAuthentication):
    form_class = SignupForm

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")

        # Check existing username/email
        if User.objects.filter(username=username).exists():
            error_message = "Username already exists. Try another."
            return self.handle_error(error_message)
        elif User.objects.filter(email=email).exists():
            error_message = "Email already exists. Try another."
            return self.handle_error(error_message)

        # Create and login user
        user = form.save(commit=False)
        user.email = email
        user.save()
        login(self.request, user)

        success_message = "Account created successfully. Welcome!"
        return self.handle_success(success_message)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Create an Account",
            "form_title": "Create Account",
            "submit_text": "Create Account",
            "data_loading_text": "Creating Account...",
            "next": self.get_success_url(),
            "extra_messages": [
                {
                    "text": "Already have an account?",
                    "link": reverse("auth:login"),
                    "link_text": "Login",
                }
            ],
        })
        return context


class LoginView(BaseAuthentication):
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Login to Your Account",
            "form_title": "Sign in",
            "submit_text": "Login",
            "data_loading_text": "Logging in...",
            "next": self.get_success_url(),
            "extra_messages": [
                {
                    "text": "Don't have an account?",
                    "link": reverse("auth:signup"),
                    "link_text": "Register",
                }
            ],
        })
        return context

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(self.request, user)
                _user = username.capitalize()
                success_message = f"Login Successful. Welcome back, {_user}!"
                return self.handle_success(success_message)
            else:
                error_message = "Your account is disabled."
                return self.handle_error(error_message)
        else:
            error_message = "Invalid username or password."
            return self.handle_error(error_message)


class LogoutView(LoginRequiredMixin, View):

    def get(self, request):
        return self._handle_logout(request)

    def post(self, request):
        return self._handle_logout(request)

    def _handle_logout(self, request):
        redirect_url = reverse("app:home")
        logout(request)
        success_message = "Successfully logged out. See you next time!"

        if is_ajax(request):
            return JsonResponse({
                "success": True,
                "message": success_message,
                "redirect_url": redirect_url,
            })

        messages.success(request, success_message)
        return redirect(redirect_url)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Custom password change view"""
    template_name = 'app/auth/password_change.html'
    success_url = reverse_lazy('app:password_change_done')


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    template_name = 'app/auth/password_reset.html'
    email_template_name = 'app/auth/password_reset_email.html'
    subject_template_name = 'app/auth/password_reset_subject.txt'
    success_url = reverse_lazy('app:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Custom password reset done view"""
    template_name = 'app/auth/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view"""
    template_name = 'app/auth/password_reset_confirm.html'
    success_url = reverse_lazy('app:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Custom password reset complete view"""
    template_name = 'app/auth/password_reset_complete.html'


class CSRFFailureView(TemplateView):
    template_name = "errors/errors.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["errors"] = f"CSRF Failure: {self.kwargs.get('reason', '')}"
        return context
