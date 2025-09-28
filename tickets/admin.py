from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'full_name', 'email', 'num_tickets', 
                    'donation_amount', 'gift_aid', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'gift_aid', 'created_at')
    search_fields = ('full_name', 'email', 'booking_reference')
    readonly_fields = ('booking_reference', 'created_at', 'updated_at', 'payment_reference')
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'full_name', 'email', 'phone_number', 'num_tickets', 'donation_amount')
        }),
        ('Payment Status', {
            'fields': ('is_paid', 'payment_reference')
        }),
        ('Gift Aid Information', {
            'fields': ('gift_aid', 'address_line1', 'address_line2', 'city', 'postcode')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def payment_reference(self, obj):
        return obj.payment_reference()
    
    payment_reference.short_description = "Payment Reference"