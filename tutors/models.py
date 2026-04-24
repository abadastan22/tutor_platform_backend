from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class TutorProfile(models.Model):
    MODE_CHOICES = (
        ("online", "Online"),
        ("offline", "Offline"),
        ("both", "Both"),
    )

    VERIFICATION_STATUS = (
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_profile",
    )

    bio = models.TextField(blank=True)
    subjects = models.ManyToManyField(Subject, related_name="tutors")
    tutoring_mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    profile_photo = models.ImageField(upload_to="tutor_photos/", blank=True, null=True)

    id_document = models.FileField(upload_to="verification_docs/", blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default="pending",
    )

    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tutor Profile - {self.user.get_full_name()}"