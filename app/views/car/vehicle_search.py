from django.views.generic import ListView, FormView
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import redirect
from django.db.models import Q

from app.models.car import Vehicle

from app.forms.search import VehicleSearchForm

User = get_user_model()


# Advanced search view
class AdvancedSearchView(FormView):
    """Advanced search form view"""
    template_name = 'app/car/advanced_search.html'
    form_class = VehicleSearchForm

    def form_valid(self, form):
        # Build query string from form data
        query_dict = {k: v for k, v in form.cleaned_data.items() if v}
        query_string = '&'.join([f"{k}={v}" for k, v in query_dict.items()])

        # Redirect to vehicle list with query params
        return redirect(f"{reverse('app:vehicle_list')}?{query_string}")


class VehicleSearchView(ListView):
    """Search view for vehicles"""
    model = Vehicle
    template_name = 'app/car/search.html'
    context_object_name = 'vehicles'
    paginate_by = 12

    def get_queryset(self):
        """Get vehicles based on search query"""
        query = self.request.GET.get('q')
        if query:
            return Vehicle.objects.filter(
                Q(title__icontains=query) |
                Q(make__icontains=query) |
                Q(model__icontains=query) |
                Q(description__icontains=query),
                live=True, published=True,
                sold=False
            ).distinct()
        return Vehicle.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['form'] = VehicleSearchForm(self.request.GET)
        return context
