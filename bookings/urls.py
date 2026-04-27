from django.urls import path
from .views import (
    BookingListCreateView,
    ScheduledSessionListView,
    TutorAvailabilityListCreateView,
    BookingDecisionView,
)
from .payment_views import (
    InitializeBookingPaymentView,
    VerifyPaystackPaymentView,
)

urlpatterns = [
    path("bookings/", BookingListCreateView.as_view()),
    path("bookings/<int:booking_id>/decision/", BookingDecisionView.as_view()),
    path("bookings/<int:booking_id>/pay/", InitializeBookingPaymentView.as_view()),
    path("payments/paystack/verify/", VerifyPaystackPaymentView.as_view()),
    path("availability/", TutorAvailabilityListCreateView.as_view()),
    path("sessions/", ScheduledSessionListView.as_view()),
]