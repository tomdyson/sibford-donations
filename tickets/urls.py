from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from .views import (
    BookingConfirmationView,
    BookingCreateView,
    BookingCreateViewV2,
    BookingReportView,
)

urlpatterns = [
    path("", BookingCreateView.as_view(), name="home"),
    path("v2/", BookingCreateViewV2.as_view(), name="home_v2"),
    path(
        "confirmation/<int:pk>/",
        BookingConfirmationView.as_view(),
        name="booking_confirmation",
    ),
    path(
        "report/",
        staff_member_required(BookingReportView.as_view()),
        name="booking_report",
    ),
]
