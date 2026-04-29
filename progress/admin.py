from django.contrib import admin
from .models import StudentGoal, ProgressNote


@admin.register(StudentGoal)
class StudentGoalAdmin(admin.ModelAdmin):
    list_display = ("id", "student_parent", "tutor", "subject", "title", "progress_percent", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("student_parent__username", "title")


@admin.register(ProgressNote)
class ProgressNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "student_parent", "tutor", "subject", "score", "created_at")
    list_filter = ("subject", "created_at")
    search_fields = ("student_parent__username", "tutor__user__username", "note")