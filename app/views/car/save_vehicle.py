from django.views.generic import ListView,  View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from django.shortcuts import get_object_or_404

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


from app.models.car import Vehicle
from app.models.cars.saved import SavedVehicle

User = get_user_model()


# Saved vehicles views
'''class SaveVehicleView(LoginRequiredMixin, View):
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
 '''


class UserSavedVehiclesView(LoginRequiredMixin, ListView):
    """List view for user's saved vehicles"""
    model = Vehicle
    template_name = 'app/car/saved_vehicles.html'
    context_object_name = 'vehicles'
    paginate_by = 12

    def get_queryset(self):
        """Get vehicles saved by the current user"""
        return Vehicle.objects.filter(
            saved_by__user=self.request.user,
            live=True, published=True
        ).order_by('-saved_by__saved_at')


class SavedVehiclesView(LoginRequiredMixin, ListView):
    """View user's saved vehicles"""
    model = SavedVehicle
    template_name = 'app/cars/saved_vehicles.html'
    context_object_name = 'saved_vehicles'
    paginate_by = 10

    def get_queryset(self):
        return SavedVehicle.objects.filter(
            user=self.request.user
        ).select_related('vehicle').order_by('-saved_at')


class SaveVehicleView(LoginRequiredMixin, View):
    """AJAX view to save/unsave a vehicle"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            data = json.loads(request.body)
            vehicle_id = data.get('vehicle_id')
            vehicle = get_object_or_404(Vehicle, id=vehicle_id)

            saved_vehicle, created = SavedVehicle.objects.get_or_create(
                user=request.user,
                vehicle=vehicle
            )

            if not created:
                saved_vehicle.delete()
                return JsonResponse({'saved': False})

            return JsonResponse({'saved': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
