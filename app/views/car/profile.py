from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from authentication.forms.auth import UserProfileForm

User = get_user_model()


class ProfileView(LoginRequiredMixin, UpdateView):
    """User profile view and update"""
    model = User
    form_class = UserProfileForm
    template_name = 'app/auth/profile.html'
    success_url = reverse_lazy('app:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['page_title'] = "Profile"
        context['user'] = user
        context['form_title'] = "Update Your Profile"
        context['submit_text'] = "Update Profile"
        context['data_loading_text'] = "Updating Profile..."
        context['extra_messages'] = [
            {
                "text": "Need help?",
                "link": reverse("app:contact"),
                "link_text": "Contact Support",
            }
        ]
        return context

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated.")
        return super().form_valid(form)
