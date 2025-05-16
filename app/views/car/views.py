from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView,
    FormView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse, HttpResponseRedirect

from app.models.car import (
    Vehicle, VehicleCategory, VehicleReview,
    SavedVehicle
)
from app.forms.search import VehicleSearchForm
from app.forms.car import VehicleReviewForm
from auth.forms.auth import UserProfileForm
from app.forms.car import VehicleForm, VehicleGalleryImageFormSet
from app.forms.contact import ContactSellerForm

User = get_user_model()


class ProfileView(LoginRequiredMixin, UpdateView):
    """User profile view and update"""
    model = User
    form_class = UserProfileForm
    template_name = 'app/auth/profile.html'
    success_url = reverse_lazy('app:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated.")
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard with listings and saved vehicles"""
    template_name = 'app/home/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # User's listed vehicles
        context['user_vehicles'] = Vehicle.objects.live().filter(
            listed_by=self.request.user
        ).order_by('-created_at')

        # User's saved vehicles
        context['saved_vehicles'] = Vehicle.objects.live().filter(
            saved_by__user=self.request.user
        ).order_by('-saved_by__saved_at')

        return context


# Vehicle Views
class VehicleListView(ListView):
    """List view for vehicles with filtering"""
    model = Vehicle
    template_name = 'app/cars/list.html'
    context_object_name = 'vehicles'
    paginate_by = 12

    def get_queryset(self):
        """Get filtered queryset based on search parameters"""
        queryset = Vehicle.objects.live().filter(published=True, sold=False)

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
        context['makes'] = Vehicle.objects.live().filter(
            published=True
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
        return Vehicle.objects.live().filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.get_object()

        # Similar vehicles (same make, model or category)
        similar_vehicles = Vehicle.objects.live().filter(
            published=True,
            sold=False
        ).exclude(id=vehicle.id)

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
        return Vehicle.objects.live().filter(
            published=True,
            sold=False,
            categories=self.category
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category

        # Add search form with category pre-selected
        initial = {'category': self.category.id}
        context['form'] = VehicleSearchForm(initial=initial)

        return context


# User Vehicle Management Views
class UserVehicleListView(LoginRequiredMixin, ListView):
    """List view for user's vehicles"""
    model = Vehicle
    template_name = 'app/car/user_vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 10

    def get_queryset(self):
        """Get vehicles listed by the current user"""
        return Vehicle.objects.live().filter(
            listed_by=self.request.user
        ).order_by('-created_at')


class UserVehicleCreateView(LoginRequiredMixin, CreateView):
    """Create view for user to add a new vehicle"""
    model = Vehicle
    form_class = VehicleForm
    template_name = 'app/car/vehicle_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['gallery_formset'] = VehicleGalleryImageFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context['gallery_formset'] = VehicleGalleryImageFormSet()
        return context

    def form_valid(self, form):
        # Set the current user as the lister
        form.instance.listed_by = self.request.user

        # Save the main form
        self.object = form.save(commit=False)

        # Process the gallery formset
        context = self.get_context_data()
        gallery_formset = context['gallery_formset']

        if gallery_formset.is_valid():
            # Save the vehicle first
            self.object.save()

            # Then save the gallery images
            gallery_formset.instance = self.object
            gallery_formset.save()

            messages.success(self.request,
                             "Vehicle listing created successfully!")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('app:vehicle_detail', kwargs={'slug': self.object.slug})


class UserVehicleUpdateView(LoginRequiredMixin,
                            UserPassesTestMixin, UpdateView):
    """Update view for user's vehicle"""
    model = Vehicle
    form_class = VehicleForm
    template_name = 'app/car/vehicle_form.html'

    def test_func(self):
        """Check if the current user is the owner of the vehicle"""
        vehicle = self.get_object()
        return vehicle.listed_by == self.request.user

    def get_context_data(self, **kwargs):
        instance = self.get_object()
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['gallery_formset'] = VehicleGalleryImageFormSet(
                self.request.POST, self.request.FILES, instance=instance
            )
        else:
            context['gallery_formset'] = (
                VehicleGalleryImageFormSet(instance=instance)
            )
        return context

    def form_valid(self, form):
        # Save the main form
        self.object = form.save(commit=False)

        # Process the gallery formset
        context = self.get_context_data()
        gallery_formset = context['gallery_formset']

        if gallery_formset.is_valid():
            # Save the vehicle first
            self.object.save()

            # Then save the gallery images
            gallery_formset.instance = self.object
            gallery_formset.save()

            messages.success(self.request,
                             "Vehicle listing updated successfully!")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('app:vehicle_detail', kwargs={'slug': self.object.slug})


class UserVehicleDeleteView(LoginRequiredMixin,
                            UserPassesTestMixin, DeleteView):
    """Delete view for user's vehicle"""
    model = Vehicle
    template_name = 'app/car/vehicle_confirm_delete.html'
    success_url = reverse_lazy('app:user_vehicle_list')

    def test_func(self):
        """Check if the current user is the owner of the vehicle"""
        vehicle = self.get_object()
        return vehicle.listed_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Vehicle listing deleted successfully.")
        return super().delete(request, *args, **kwargs)


# Review views
class AddVehicleReviewView(LoginRequiredMixin, CreateView):
    """Create view for adding a review to a vehicle"""
    model = VehicleReview
    form_class = VehicleReviewForm
    template_name = 'app/car/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle'] = get_object_or_404(
            Vehicle, slug=self.kwargs['slug'], published=True
        )
        return context

    def form_valid(self, form):
        # Set the user and vehicle
        form.instance.user = self.request.user
        form.instance.vehicle = get_object_or_404(
            Vehicle, slug=self.kwargs['slug'], published=True
        )

        # Check if user already reviewed this vehicle
        existing_review = VehicleReview.objects.filter(
            user=self.request.user,
            vehicle=form.instance.vehicle
        ).exists()

        if existing_review:
            messages.error(self.request,
                           "You have already reviewed this vehicle.")
            return redirect('app:vehicle_detail', slug=self.kwargs['slug'])

        messages.success(
            self.request,
            "Thank you for your review! It will be visible after approval."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app:vehicle_detail',
                       kwargs={'slug': self.kwargs['slug']})


# Saved vehicles views
class SaveVehicleView(LoginRequiredMixin, View):
    """View for saving/unsaving a vehicle"""
    def post(self, request, *args, **kwargs):
        vehicle = get_object_or_404(Vehicle, slug=kwargs['slug'],
                                    published=True)
        saved = SavedVehicle.objects.filter(user=request.user,
                                            vehicle=vehicle).exists()

        if saved:
            # Unsave the vehicle
            SavedVehicle.objects.filter(user=request.user,
                                        vehicle=vehicle).delete()
            status = 'unsaved'
            message = "Vehicle removed from your saved listings."
        else:
            # Save the vehicle
            SavedVehicle.objects.create(user=request.user, vehicle=vehicle)
            status = 'saved'
            message = "Vehicle saved to your profile."

        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': status,
                'message': message
            })

        # Regular request
        messages.success(request, message)
        return redirect('app:vehicle_detail', slug=kwargs['slug'])


class UserSavedVehiclesView(LoginRequiredMixin, ListView):
    """List view for user's saved vehicles"""
    model = Vehicle
    template_name = 'app/car/saved_vehicles.html'
    context_object_name = 'vehicles'
    paginate_by = 12

    def get_queryset(self):
        """Get vehicles saved by the current user"""
        return Vehicle.objects.live().filter(
            saved_by__user=self.request.user,
            published=True
        ).order_by('-saved_by__saved_at')


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
            return Vehicle.objects.live().filter(
                Q(title__icontains=query) |
                Q(make__icontains=query) |
                Q(model__icontains=query) |
                Q(description__icontains=query),
                published=True,
                sold=False
            ).distinct()
        return Vehicle.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['form'] = VehicleSearchForm(self.request.GET)
        return context
