from django.views.generic import FormView
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages


from app.models.car import Vehicle

from app.forms.contact import ContactSellerForm

User = get_user_model()


class ContactSellerView(FormView):
    """Contact form for vehicle sellers"""
    form_class = ContactSellerForm
    template_name = 'app/cars/contact_seller.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle'] = get_object_or_404(Vehicle,
                                               pk=self.kwargs['vehicle_pk'])
        return context

    def form_valid(self, form):
        vehicle = get_object_or_404(Vehicle, pk=self.kwargs['vehicle_pk'])

        # Send email to seller (implement email sending logic)
        # For now, just show a success message
        _tt = vehicle.title
        messages.success(
            self.request,
            f'Your message about the {_tt} has been sent to the seller!'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app:car_detail',
                       kwargs={'pk': self.kwargs['vehicle_pk']})
