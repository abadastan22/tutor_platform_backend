from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("student_parent", "Student/Parent"),
        ("tutor", "Tutor"),
        ("admin", "Admin"),
    )

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=30, blank=True)