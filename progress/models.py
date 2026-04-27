from django.conf import settings
from django.db import models

from bookings.models import ScheduledSession
from tutors.models import Subject, TutorProfile


class StudentGoal(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
    )

    student_parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_goals",
    )
    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_goals",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_goals",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_date = models.DateField(null=True, blank=True)
    progress_percent = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)


class ProgressNote(models.Model):
    student_parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress_notes",
    )
    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.CASCADE,
        related_name="progress_notes",
    )
    session = models.ForeignKey(
        ScheduledSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="progress_notes",
    )
    subject = models.CharField(max_length=120)
    note = models.TextField()
    homework = models.TextField(blank=True)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)