from django.urls import path
from .views import (
    AdminStatsView,
    AdminPendingTutorsView,
    AdminBookingsView,
    AdminUsersView,
    AdminUserStatusView,
)

urlpatterns = [
    path("stats/", AdminStatsView.as_view()),
    path("pending-tutors/", AdminPendingTutorsView.as_view()),
    path("bookings/", AdminBookingsView.as_view()),
    path("users/", AdminUsersView.as_view()),
    path("users/<int:user_id>/status/", AdminUserStatusView.as_view()),
]