from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
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
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValueError("Rating must be between 1 and 5.")

        minimum_review_date = self.booking.start_date + timedelta(days=30)

        if timezone.now().date() < minimum_review_date:
            raise ValueError("You can only review a tutor after 30 days.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        tutor = self.booking.tutor
        reviews = Review.objects.filter(booking__tutor=tutor)
        tutor.total_reviews = reviews.count()
        tutor.average_rating = sum(r.rating for r in reviews) / tutor.total_reviews
        tutor.save()