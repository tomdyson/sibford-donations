from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView
from django.contrib import messages

from .models import Booking
from .forms import BookingForm


class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'tickets/booking_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggested_donation'] = self.form_class.SUGGESTED_DONATION
        return context
    
    def form_valid(self, form):
        # Save the booking to the database
        self.object = form.save()
        
        # Add a success message
        messages.success(self.request, "Your booking was successful!")
        
        # Redirect to the confirmation page with the booking ID
        return redirect('booking_confirmation', pk=self.object.id)


class BookingConfirmationView(TemplateView):
    template_name = 'tickets/booking_confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get('pk')
        try:
            booking = Booking.objects.get(id=booking_id)
            context['booking'] = booking
            context['payment_reference'] = booking.payment_reference()
            context['bank_details'] = {
                'account_name': 'Sibford Fundraising',
                'sort_code': '12-34-56',
                'account_number': '12345678',
                'reference': booking.payment_reference(),
            }
        except Booking.DoesNotExist:
            messages.error(self.request, "Booking not found.")
            context['error'] = "Booking information not found."
        
        return context


# No longer needed since we're using the BookingCreateView directly at the root URL