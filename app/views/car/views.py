from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import Http404

from app.models.car import Vehicle
from app.models.cars.category import VehicleCategory
from app.models.cars.review import VehicleReview
from app.models.cars.saved import SavedVehicle

from app.forms.search import VehicleSearchForm
from app.forms.car import (
    VehicleReviewForm, VehicleForm
)

from app.forms.contact import ContactSellerForm

User = get_user_model()


# Vehicle Views
class VehicleListView(ListView):
    """List view for vehicles with filtering"""
    model = Vehicle
    template_name = 'app/cars/list.html'
    context_object_name = 'vehicles'
    paginate_by = 12

    def get_queryset(self):
        """Get filtered queryset based on search parameters"""
        queryset = Vehicle.objects.filter(
            live=True, published=True, sold=False)

        # Apply search form filters
        form = VehicleSearchForm(self.request.GET)
        if form.is_valid():
            filters = {}

            # Price range
            if form.cleaned_data.get('min_price'):
                filters['price__gte'] = form.cleaned_data['min_price']
            if form.cleaned_data.get('max_price'):
                filters['price__lte'] = form.cleaned_data['max_price']

            # Year range
            if form.cleaned_data.get('min_year'):
                filters['year__gte'] = form.cleaned_data['min_year']
            if form.cleaned_data.get('max_year'):
                filters['year__lte'] = form.cleaned_data['max_year']

            # Other filters
            for field in ['make', 'model', 'transmission', 'fuel_type',
                          'color', 'condition']:
                if form.cleaned_data.get(field):
                    filters[field] = form.cleaned_data[field]

            # Categories
            if form.cleaned_data.get('category'):
                filters['categories'] = form.cleaned_data['category']

            # Apply filters
            queryset = queryset.filter(**filters)

            # Search term
            if form.cleaned_data.get('search'):
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(title__icontains=search_term) |
                    Q(make__icontains=search_term) |
                    Q(model__icontains=search_term) |
                    Q(description__icontains=search_term)
                )

        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        valid_sorts = {
            'price': 'price',
            '-price': '-price',
            'year': 'year',
            '-year': '-year',
            'mileage': 'mileage',
            '-mileage': '-mileage',
            'created_at': 'created_at',
            '-created_at': '-created_at',
        }

        if sort in valid_sorts:
            queryset = queryset.order_by(valid_sorts[sort])
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add search form to context
        context['form'] = VehicleSearchForm(self.request.GET)

        # Add categories for sidebar
        context['categories'] = VehicleCategory.objects.annotate(
            count=Count('vehicles', filter=Q(vehicles__live=True,
                                             vehicles__published=True))
        ).filter(count__gt=0)

        # Add filters
        context['makes'] = Vehicle.objects.filter(
            live=True, published=True
        ).values_list('make', flat=True).distinct().order_by('make')

        # Get current URL parameters for maintaining filters in pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['current_filters'] = get_params.urlencode()

        return context


class VehicleDetailView(DetailView):
    """Detail view for a vehicle"""
    model = Vehicle
    template_name = 'app/cars/details.html'
    context_object_name = 'vehicle'

    def get_queryset(self):
        """Only show published vehicles"""
        return Vehicle.objects.filter(live=True, published=True)

    def get_this_object(self, queryset=None):
        """Get the vehicle object, ensuring it's published"""
        obj = super().get_object(queryset)
        if not obj.objects.exists():
            raise Http404("Vehicle not found or not published.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        vehicle = self.get_this_object()

        # Similar vehicles (same make, model or category)
        similar_vehicles = queryset.exclude(pk=vehicle.pk)

        # Try to find by same make and model first
        similar_by_model = similar_vehicles.filter(
            make=vehicle.make,
            model=vehicle.model
        )[:4]

        # If not enough, add vehicles from same make
        if similar_by_model.count() < 4:
            similar_by_make = similar_vehicles.filter(
                make=vehicle.make
            ).exclude(id__in=similar_by_model.values_list('id', flat=True))

            # Combine both querysets
            similar_vehicles = list(similar_by_model) + list(similar_by_make)
            # Trim to 4 items
            similar_vehicles = similar_vehicles[:4]
        else:
            similar_vehicles = similar_by_model

        context['similar_vehicles'] = similar_vehicles

        # Reviews
        context['reviews'] = (
            vehicle.reviews.filter(approved=True).order_by('-created_at')
        )
        context['review_avg'] = (
            context['reviews'].aggregate(Avg('rating'))['rating__avg']
        )
        context['review_count'] = context['reviews'].count()

        # Check if user has saved this vehicle
        if self.request.user.is_authenticated:
            context['is_saved'] = SavedVehicle.objects.filter(
                user=self.request.user,
                vehicle=vehicle
            ).exists()

            # Check if user has already reviewed this vehicle
            context['user_has_reviewed'] = VehicleReview.objects.filter(
                user=self.request.user,
                vehicle=vehicle
            ).exists()

            # Review form for authenticated users
            if not context['user_has_reviewed']:
                context['review_form'] = VehicleReviewForm()

        # Contact seller form
        context['contact_form'] = ContactSellerForm(initial={
            'subject': f"Inquiry about {vehicle}",
            'vehicle': vehicle.id
        })

        return context


class CategoryVehicleListView(ListView):
    """List view for vehicles in a specific category"""
    model = Vehicle
    template_name = 'app/car/category_list.html'
    context_object_name = 'vehicles'
    paginate_by = 12

    def get_queryset(self):
        """Get vehicles in the selected category"""
        self.category = get_object_or_404(VehicleCategory,
                                          slug=self.kwargs['slug'])
        return Vehicle.objects.filter(live=True, published=True,
                                      sold=False, categories=self.category
                                      ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category

        # Add search form with category pre-selected
        # initial = {'category': self.category.slug}
        context['form'] = VehicleSearchForm()

        return context


class VehicleCreateView(LoginRequiredMixin, CreateView):
    """Create a new vehicle listing"""
    model = Vehicle
    form_class = VehicleForm
    template_name = 'app/cars/create.html'
    context_object_name = 'vehicle'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        vehicle = form.instance
        vehicle.listed_by = self.request.user
        self.object = vehicle
        vehicle.save()
        messages.success(self.request, 'Vehicle listing created successfully!')
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        """Redirect to the vehicle detail page after creation"""
        return reverse_lazy('app:car_detail', kwargs={'pk': self.object.pk})


class VehicleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing vehicle listing"""
    model = Vehicle
    form_class = VehicleForm
    template_name = 'app/cars/update.html'

    def test_func(self):
        vehicle = self.object
        # return self.request.user == vehicle.listed_b
        #  or self.request.user.is_staff
        return self.request.user == self.request.user.is_staff or\
            vehicle.listed_by

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        vehicle = form.instance
        self.object = vehicle
        vehicle.save()
        messages.success(self.request, 'Vehicle listing updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app:car_detail', kwargs={'pk': self.object.pk})


class VehicleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a vehicle listing"""
    model = Vehicle
    template_name = 'app/cars/delete.html'
    success_url = reverse_lazy('app:dashboard')

    def test_func(self):
        vehicle = self.get_object()
        return self.request.user == vehicle.listed_by or\
            self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Vehicle listing deleted successfully!')
        return super().delete(request, *args, **kwargs)
