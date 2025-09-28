from django.urls import path
from .views import BookingCreateView, BookingConfirmationView, BookingReportView
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    path('', BookingCreateView.as_view(), name='home'),
    path('confirmation/<int:pk>/', BookingConfirmationView.as_view(), name='booking_confirmation'),
    path('report/', staff_member_required(BookingReportView.as_view()), name='booking_report'),
]