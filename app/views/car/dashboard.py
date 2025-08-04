from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from app.models.car import Vehicle

User = get_user_model()


class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard with listings and saved vehicles"""
    template_name = 'app/home/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # User's listed vehicles
        context['user_vehicles'] = Vehicle.objects.filter(
            live=True, listed_by=self.request.user
        ).order_by('-created_at')

        # User's saved vehicles
        context['saved_vehicles'] = Vehicle.objects.filter(
            live=True, saved_by__user=self.request.user
        ).order_by('-saved_by__saved_at')

        return context
