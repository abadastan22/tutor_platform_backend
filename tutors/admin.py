from django.contrib import admin
from .models import Subject, TutorProfile


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "tutoring_mode",
        "city",
        "state",
        "hourly_rate",
        "verification_status",
        "average_rating",
        "total_reviews",
        "created_at",
    )
    list_filter = ("verification_status", "tutoring_mode", "city", "state")
    search_fields = ("user__username", "user__email", "city", "state")
    filter_horizontal = ("subjects",)