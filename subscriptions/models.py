from django.conf import settings
from django.db import models
from tutors.models import TutorProfile


class SubscriptionPlan(models.Model):
    INTERVAL_CHOICES = (
        ("week", "Week"),
        ("month", "Month"),
    )

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.CASCADE,
        related_name="subscription_plans",
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES, default="month")
    sessions_per_interval = models.PositiveIntegerField(default=4)
    stripe_price_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    STATUS_CHOICES = (
        ("incomplete", "Incomplete"),
        ("active", "Active"),
        ("past_due", "Past Due"),
        ("cancelled", "Cancelled"),
        ("unpaid", "Unpaid"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="user_subscriptions",
    )
    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_subscriptions",
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="incomplete")
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)