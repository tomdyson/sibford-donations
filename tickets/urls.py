from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from .views import (
    BookingConfirmationView,
    BookingCreateView,
    BookingCreateViewV2,
    BookingCreateViewV3,
    BookingReportView,
)

urlpatterns = [
    path("", BookingCreateViewV3.as_view(), name="home"),
    path("v1/", BookingCreateView.as_view(), name="home_v1"),
    path("v2/", BookingCreateViewV2.as_view(), name="home_v2"),
    path("v3/", BookingCreateViewV3.as_view(), name="home_v3"),
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
