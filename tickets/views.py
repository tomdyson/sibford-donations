from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView

from .forms import BookingForm, BookingFormV2, BookingFormV3, ReportFilterForm
from .models import Booking
from .utils import send_admin_notification_email, send_booking_confirmation_email


class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "tickets/booking_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["suggested_donation"] = self.form_class.SUGGESTED_DONATION
        return context

    def form_valid(self, form):
        # Save the booking to the database
        self.object = form.save()

        # Send confirmation email to the customer
        email_sent = send_booking_confirmation_email(self.request, self.object)
        if email_sent:
            messages.success(
                self.request,
                "Your booking was successful! A confirmation email has been sent.",
            )
        else:
            messages.warning(
                self.request,
                "Your booking was successful, but there was an issue sending the confirmation email.",
            )

        # Send notification email to admins
        send_admin_notification_email(self.request, self.object)

        # Redirect to the confirmation page with the booking ID
        return redirect("booking_confirmation", pk=self.object.id)


class BookingCreateViewV2(CreateView):
    """Version 2: Fixed £25 per ticket + optional extra donation."""

    model = Booking
    form_class = BookingFormV2
    template_name = "tickets/booking_form_v2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ticket_price"] = self.form_class.TICKET_PRICE
        return context

    def form_valid(self, form):
        # Check for duplicate submissions (same email within last 60 seconds)
        email = form.cleaned_data.get("email")
        num_tickets = form.cleaned_data.get("num_tickets")
        donation_amount = num_tickets * self.form_class.TICKET_PRICE + (
            form.cleaned_data.get("extra_donation") or 0
        )

        # Look for recent bookings with same email, tickets, and donation amount
        cutoff_time = timezone.now() - timedelta(seconds=60)
        recent_duplicate = Booking.objects.filter(
            email=email,
            num_tickets=num_tickets,
            donation_amount=donation_amount,
            created_at__gte=cutoff_time,
        ).first()

        if recent_duplicate:
            # Redirect to the existing booking's confirmation page
            messages.info(
                self.request,
                "This booking was already submitted. Showing your confirmation details.",
            )
            return redirect("booking_confirmation", pk=recent_duplicate.id)

        # Save the booking to the database
        self.object = form.save()

        # Send confirmation email to the customer
        email_sent = send_booking_confirmation_email(self.request, self.object)
        if email_sent:
            messages.success(
                self.request,
                "Your booking was successful! A confirmation email has been sent.",
            )
        else:
            messages.warning(
                self.request,
                "Your booking was successful, but there was an issue sending the confirmation email.",
            )

        # Send notification email to admins
        send_admin_notification_email(self.request, self.object)

        # Redirect to the confirmation page with the booking ID
        return redirect("booking_confirmation", pk=self.object.id)


class BookingCreateViewV3(CreateView):
    """Version 3: Fixed £20 per ticket + separate optional extra donation field."""

    model = Booking
    form_class = BookingFormV3
    template_name = "tickets/booking_form_v3.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ticket_price"] = self.form_class.TICKET_PRICE
        return context

    def form_valid(self, form):
        # Check for duplicate submissions (same email within last 60 seconds)
        email = form.cleaned_data.get("email")
        num_tickets = form.cleaned_data.get("num_tickets")
        donation_amount = num_tickets * self.form_class.TICKET_PRICE + (
            form.cleaned_data.get("extra_donation") or 0
        )

        # Look for recent bookings with same email, tickets, and donation amount
        cutoff_time = timezone.now() - timedelta(seconds=60)
        recent_duplicate = Booking.objects.filter(
            email=email,
            num_tickets=num_tickets,
            donation_amount=donation_amount,
            created_at__gte=cutoff_time,
        ).first()

        if recent_duplicate:
            # Redirect to the existing booking's confirmation page
            messages.info(
                self.request,
                "This booking was already submitted. Showing your confirmation details.",
            )
            return redirect("booking_confirmation", pk=recent_duplicate.id)

        # Save the booking to the database
        self.object = form.save()

        # Send confirmation email to the customer
        email_sent = send_booking_confirmation_email(self.request, self.object)
        if email_sent:
            messages.success(
                self.request,
                "Your booking was successful! A confirmation email has been sent.",
            )
        else:
            messages.warning(
                self.request,
                "Your booking was successful, but there was an issue sending the confirmation email.",
            )

        # Send notification email to admins
        send_admin_notification_email(self.request, self.object)

        # Redirect to the confirmation page with the booking ID
        return redirect("booking_confirmation", pk=self.object.id)


class BookingConfirmationView(TemplateView):
    template_name = "tickets/booking_confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get("pk")
        try:
            booking = Booking.objects.get(id=booking_id)
            context["booking"] = booking
            context["payment_reference"] = booking.payment_reference()
            # Use bank details from settings
            context["bank_details"] = {
                **settings.BANK_DETAILS,
                "reference": booking.payment_reference(),
            }
        except Booking.DoesNotExist:
            messages.error(self.request, "Booking not found.")
            context["error"] = "Booking information not found."

        return context


# No longer needed since we're using the BookingCreateView directly at the root URL


class BookingReportView(ListView):
    model = Booking
    template_name = "tickets/booking_report.html"
    context_object_name = "bookings"
    paginate_by = 20

    def get_queryset(self):
        queryset = Booking.objects.all().order_by("-created_at")

        # Apply filters from form
        form = ReportFilterForm(self.request.GET)
        if form.is_valid():
            # Filter by payment status
            payment_status = form.cleaned_data.get("payment_status")
            if payment_status == "paid":
                queryset = queryset.filter(is_paid=True)
            elif payment_status == "unpaid":
                queryset = queryset.filter(is_paid=False)

            # Filter by gift aid status
            gift_aid = form.cleaned_data.get("gift_aid")
            if gift_aid == "yes":
                queryset = queryset.filter(gift_aid=True)
            elif gift_aid == "no":
                queryset = queryset.filter(gift_aid=False)

            # Search by name or email
            search_query = form.cleaned_data.get("search")
            if search_query:
                queryset = queryset.filter(
                    Q(full_name__icontains=search_query)
                    | Q(email__icontains=search_query)
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter form to context
        form = ReportFilterForm(self.request.GET or None)
        context["filter_form"] = form

        # Add summary statistics
        bookings = self.get_queryset()
        context["total_bookings"] = bookings.count()
        context["total_tickets"] = (
            bookings.aggregate(Sum("num_tickets"))["num_tickets__sum"] or 0
        )
        context["total_amount"] = (
            bookings.aggregate(Sum("donation_amount"))["donation_amount__sum"] or 0
        )
        context["paid_amount"] = (
            bookings.filter(is_paid=True).aggregate(Sum("donation_amount"))[
                "donation_amount__sum"
            ]
            or 0
        )
        context["unpaid_amount"] = (
            bookings.filter(is_paid=False).aggregate(Sum("donation_amount"))[
                "donation_amount__sum"
            ]
            or 0
        )
        context["gift_aid_count"] = bookings.filter(gift_aid=True).count()

        # Make booking references available for all bookings in the template
        for booking in context["bookings"]:
            booking.ref = booking.booking_reference()

        return context
