from django.views.generic import (
   ListView, CreateView, UpdateView, DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect


from app.models.car import (
    Vehicle
)
from app.forms.car import (
    VehicleForm, VehicleGalleryImageFormSet
)
User = get_user_model()


# User Vehicle Management Views
class UserVehicleListView(LoginRequiredMixin, ListView):
    """List view for user's vehicles"""
    model = Vehicle
    template_name = 'app/car/user_vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 10

    def get_queryset(self):
        """Get vehicles listed by the current user"""
        return Vehicle.objects.filter(live=True,
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
        return vehicle.objects.filter(
            live=True, listed_by=self.request.user
        ).exists()

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
        return vehicle.objects.filter(
            live=True, listed_by=self.request.user
        ).exists()

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Vehicle listing deleted successfully.")
        return super().delete(request, *args, **kwargs)


class UserVehiclesView(LoginRequiredMixin, ListView):
    """View user's vehicle listings"""
    model = Vehicle
    template_name = 'app/cars/user_vehicles.html'
    context_object_name = 'vehicles'
    paginate_by = 10

    def get_queryset(self):
        return Vehicle.objects.filter(
            live=True, listed_by=self.request.user
        ).order_by('-created_at')
