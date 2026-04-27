from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from bookings.models import Booking


class Review(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="review",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")

        if self.booking.student_parent != self.reviewer:
            raise ValidationError("You can only review your own booking.")

        if self.booking.status != "completed":
            raise ValidationError("Only completed bookings can be reviewed.")

        earliest_review_date = self.booking.start_date + timedelta(days=30)

        if timezone.now().date() < earliest_review_date:
            raise ValidationError("You can only review a tutor after 30 days.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        tutor = self.booking.tutor
        reviews = Review.objects.filter(booking__tutor=tutor)

        tutor.total_reviews = reviews.count()
        tutor.average_rating = round(
            sum(review.rating for review in reviews) / tutor.total_reviews,
            2,
        )
        tutor.save()