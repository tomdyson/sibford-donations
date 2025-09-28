from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, ListView
from django.contrib import messages
from django.db.models import Q, Sum

from .models import Booking
from .forms import BookingForm, ReportFilterForm



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


class BookingReportView(ListView):
    model = Booking
    template_name = 'tickets/booking_report.html'
    context_object_name = 'bookings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Booking.objects.all().order_by('-created_at')
        
        # Apply filters from form
        form = ReportFilterForm(self.request.GET)
        if form.is_valid():
            # Filter by payment status
            payment_status = form.cleaned_data.get('payment_status')
            if payment_status == 'paid':
                queryset = queryset.filter(is_paid=True)
            elif payment_status == 'unpaid':
                queryset = queryset.filter(is_paid=False)
            
            # Filter by gift aid status
            gift_aid = form.cleaned_data.get('gift_aid')
            if gift_aid == 'yes':
                queryset = queryset.filter(gift_aid=True)
            elif gift_aid == 'no':
                queryset = queryset.filter(gift_aid=False)
            
            # Search by name or email
            search_query = form.cleaned_data.get('search')
            if search_query:
                queryset = queryset.filter(
                    Q(full_name__icontains=search_query) |
                    Q(email__icontains=search_query)
                )
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter form to context
        form = ReportFilterForm(self.request.GET or None)
        context['filter_form'] = form
        
        # Add summary statistics
        bookings = self.get_queryset()
        context['total_bookings'] = bookings.count()
        context['total_tickets'] = bookings.aggregate(Sum('num_tickets'))['num_tickets__sum'] or 0
        context['total_amount'] = bookings.aggregate(Sum('donation_amount'))['donation_amount__sum'] or 0
        context['paid_amount'] = bookings.filter(is_paid=True).aggregate(Sum('donation_amount'))['donation_amount__sum'] or 0
        context['unpaid_amount'] = bookings.filter(is_paid=False).aggregate(Sum('donation_amount'))['donation_amount__sum'] or 0
        context['gift_aid_count'] = bookings.filter(gift_aid=True).count()
        
        # Make booking references available for all bookings in the template
        for booking in context['bookings']:
            booking.ref = booking.booking_reference()
        
        return context