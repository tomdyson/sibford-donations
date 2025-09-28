from django.urls import path
from .views import BookingCreateView, BookingConfirmationView

urlpatterns = [
    path('', BookingCreateView.as_view(), name='home'),
    path('confirmation/<int:pk>/', BookingConfirmationView.as_view(), name='booking_confirmation'),
]