from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    # Define suggested donation amount
    SUGGESTED_DONATION = 25

    # Override the donation_amount field to set initial value
    donation_amount = forms.DecimalField(
        label="Donation Amount (£)",
        min_value=1,
        decimal_places=2,
        initial=SUGGESTED_DONATION,
        help_text=f"Suggested donation: £{SUGGESTED_DONATION} per ticket",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500',
            'min': 1,
            'step': '0.01'
        })
    )

    # Add a field to confirm Gift Aid eligibility
    gift_aid_confirmation = forms.BooleanField(
        required=False,
        label="I confirm that I am a UK taxpayer and understand that if I pay less Income Tax and/or "
              "Capital Gains Tax than the amount of Gift Aid claimed on all my donations in that tax "
              "year it is my responsibility to pay any difference.",
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-stone-300 text-stone-600 focus:ring-stone-500 mr-2'
        })
    )

    class Meta:
        model = Booking
        fields = [
            'full_name', 'email', 'phone_number', 'num_tickets',
            'donation_amount', 'gift_aid',
            'address_line1', 'address_line2', 'city', 'postcode'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500'}),
            'num_tickets': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500', 'min': 1}),
            'donation_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500', 'min': 1}),
            'gift_aid': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-stone-300 text-stone-600 focus:ring-stone-500 mr-2'}),
            'address_line1': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500'}),
            'address_line2': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500'}),
            'postcode': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make address fields conditionally required based on gift_aid
        self.fields['address_line1'].required = False
        self.fields['city'].required = False
        self.fields['postcode'].required = False

        # Update donation amount when number of tickets changes
        initial_tickets = self.initial.get('num_tickets', 1)
        self.fields['donation_amount'].initial = self.SUGGESTED_DONATION * initial_tickets

    def clean(self):
        cleaned_data = super().clean()
        gift_aid = cleaned_data.get('gift_aid')

        # If gift aid is selected, make sure address fields are provided
        if gift_aid:
            for field in ['address_line1', 'city', 'postcode']:
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required when Gift Aid is selected")
                    self.fields[field].widget.attrs.update({'class': self.fields[field].widget.attrs.get('class', '') + ' border-rose-300 text-rose-900 placeholder-rose-300 focus:ring-rose-500 focus:border-rose-500'})

            # Also check that gift_aid_confirmation is checked
            if not cleaned_data.get('gift_aid_confirmation'):
                self.add_error('gift_aid_confirmation',
                              "You must confirm the Gift Aid declaration to proceed with Gift Aid")
                self.fields['gift_aid_confirmation'].widget.attrs.update({'class': self.fields['gift_aid_confirmation'].widget.attrs.get('class', '') + ' border-rose-300'})

        return cleaned_data


class ReportFilterForm(forms.Form):
    """Form for filtering the booking report."""
    PAYMENT_STATUS_CHOICES = (
        ('', 'All Bookings'),
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    )

    GIFT_AID_CHOICES = (
        ('', 'All Bookings'),
        ('yes', 'With Gift Aid'),
        ('no', 'Without Gift Aid'),
    )

    payment_status = forms.ChoiceField(
        choices=PAYMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500'
        })
    )

    gift_aid = forms.ChoiceField(
        choices=GIFT_AID_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500'
        })
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-stone-300 rounded-md focus:ring-2 focus:ring-stone-500 focus:border-stone-500',
            'placeholder': 'Search by name or email'
        })
    )
