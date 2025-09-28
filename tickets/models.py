from django.db import models

class Booking(models.Model):
    """Model representing a ticket booking."""
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    num_tickets = models.PositiveIntegerField(default=1)
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gift_aid = models.BooleanField(default=False)
    
    # Gift Aid information (only required if gift_aid is True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    
    # Booking status
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking {self.booking_reference()} - {self.full_name}"
    
    def total_amount(self):
        """Calculate the total donation amount."""
        return self.donation_amount
    
    def booking_reference(self):
        """Generate a booking reference from the ID."""
        return f"SIB-{self.id}"
        
    def payment_reference(self):
        """Generate a payment reference from the booking ID."""
        return f"SIB-{self.id}"