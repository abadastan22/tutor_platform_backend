from django.contrib import admin
from .models import Booking, TutorAvailability, ScheduledSession


@admin.register(TutorAvailability)
class TutorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("id", "tutor", "day_of_week", "start_time", "end_time", "is_active")
    list_filter = ("day_of_week", "is_active")
    search_fields = ("tutor__user__username",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student_parent",
        "tutor",
        "subject",
        "tutoring_mode",
        "start_date",
        "start_time",
        "status",
        "payment_status",
        "amount",
        "created_at",
    )
    list_filter = ("status", "payment_status", "tutoring_mode", "start_date")
    search_fields = ("student_parent__username", "tutor__user__username", "subject")


@admin.register(ScheduledSession)
class ScheduledSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "tutor",
        "student_parent",
        "session_date",
        "start_time",
        "end_time",
        "is_completed",
    )
    list_filter = ("session_date", "is_completed")
    search_fields = ("student_parent__username", "tutor__user__username", "booking__subject")