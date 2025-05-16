from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.db.models import Count, Q
from django.views.generic.edit import FormView
# from django.views.generic.edit import FormView

from app.models.car import Vehicle, VehicleCategory
from app.forms.search import VehicleSearchForm


class HomeView(TemplateView):
    template_name = "app/home/home.html"
    status = 200

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Featured vehicles
        context['featured_vehicles'] = Vehicle.objects.live().filter(
            published=True,
            featured=True,
            sold=False
        )[:6]

        # Latest vehicles
        context['latest_vehicles'] = Vehicle.objects.live().filter(
            published=True,
            sold=False
        ).order_by('-first_published_at')[:8]

        # Popular categories with vehicle count
        context['categories'] = VehicleCategory.objects.annotate(
            vehicle_count=Count('vehicles', filter=Q(vehicles__live=True,
                                                     vehicles__published=True))
        ).filter(vehicle_count__gt=0).order_by('-vehicle_count')[:8]

        # Search form
        context['search_form'] = VehicleSearchForm()

        return context


class AboutView(TemplateView):
    template_name = "app/about/about.html"
    status = 200

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "About Us",
            "form_title": "Learn More About Us",
            "submit_text": "Discover",
            "data_loading_text": "Loading...",
            "extra_messages": [
                {
                    "text": "Have questions?",
                    "link": "/contact/",
                    "link_text": "Contact Us",
                }
            ],
        })
        return context


class ContactView(FormView):
    template_name = "app/contact/contact.html"
    status = 200

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Contact Us",
            "form_title": "Get in Touch",
            "submit_text": "Send Message",
            "data_loading_text": "Sending...",
            "extra_messages": [
                {
                    "text": "Need assistance?",
                    "link": "/help/",
                    "link_text": "Help Center",
                }
            ],
        })
        return context

    def form_valid(self, form):
        return super().form_valid(form)


class HelpView(TemplateView):
    template_name = "app/help/help.html"
    status = 200

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Help Center",
            "form_title": "How Can We Assist You?",
            "submit_text": "Get Help",
            "data_loading_text": "Loading...",
            "extra_messages": [
                {
                    "text": "Need further assistance?",
                    "link": "/contact/",
                    "link_text": "Contact Us",
                }
            ],
        })
        return context


class ServicesView(TemplateView):
    template_name = "app/services/services.html"
    status = 200


class CustomRedirectView(RedirectView):
    """
    Custom redirect view to handle redirects with custom messages.
    """
    permanent = True
    query_string = True
    redirect_to = "/"  # Default redirect URL
    status_code = 302

    def get_redirect_url(self, *args, **kwargs):
        """
        Override the get_redirect_url method to customize the redirect URL.
        """
        # Custom logic to determine the redirect URL

        redirect_to = self.redirect_to

        query_params = self.request.GET.urlencode()
        if query_params:
            return f"{redirect_to}?{query_params}"
        return redirect_to
