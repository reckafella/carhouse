from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib import messages
from django.urls import reverse

from app.models.car import Vehicle
from app.models.cars.review import VehicleReview

from app.forms.car import VehicleReviewForm


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


class VehicleReviewCreateView(LoginRequiredMixin, CreateView):
    """Create a review for a vehicle"""
    model = VehicleReview
    form_class = VehicleReviewForm
    template_name = 'app/cars/add_review.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['vehicle'] = get_object_or_404(Vehicle,
                                              pk=self.kwargs['vehicle_pk'])
        return kwargs

    def form_valid(self, form):
        vehicle = get_object_or_404(Vehicle, pk=self.kwargs['vehicle_pk'])
        form.instance.user = self.request.user
        form.instance.vehicle = vehicle
        messages.success(self.request,
                         'Review submitted successfully!\
                            It will be displayed after approval.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app:car_detail',
                       kwargs={'pk': self.kwargs['vehicle_pk']})
