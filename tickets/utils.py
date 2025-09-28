from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

from .models import Booking


def send_booking_confirmation_email(request, booking):
    """
    Send a booking confirmation email to the customer.
    
    Args:
        request: The HTTP request object
        booking: The Booking instance
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = f'Booking Confirmation - Sibford CATS Event - Reference: {booking.booking_reference()}'
    
    # Prepare context for email template
    context = {
        'booking': booking,
        'payment_reference': booking.payment_reference(),
        'bank_details': settings.BANK_DETAILS,
    }
    
    # Render HTML message
    html_message = render_to_string('tickets/emails/booking_confirmation.html', context)
    
    # Create plain text version by stripping HTML tags
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error
        print(f"Error sending booking confirmation email: {str(e)}")
        return False


def send_admin_notification_email(request, booking):
    """
    Send a notification email to admins when a new booking is received.
    
    Args:
        request: The HTTP request object
        booking: The Booking instance
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = f'New Booking Notification - {booking.full_name} - {booking.num_tickets} tickets'
    
    # Get the admin URL (this is an approximation, adjust as needed)
    if request:
        site = get_current_site(request)
        domain = site.domain
        protocol = 'https' if request.is_secure() else 'http'
        admin_url = f"{protocol}://{domain}/admin/tickets/booking/{booking.id}/change/"
    else:
        admin_url = "#"  # Fallback if no request object is provided
    
    # Prepare context for email template
    context = {
        'booking': booking,
        'payment_reference': booking.payment_reference(),
        'admin_url': admin_url,
    }
    
    # Render HTML message
    html_message = render_to_string('tickets/emails/admin_notification.html', context)
    
    # Create plain text version by stripping HTML tags
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ADMIN_NOTIFICATION_EMAILS,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error
        print(f"Error sending admin notification email: {str(e)}")
        return False