from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "student_parent",
            "tutor",
            "subject",
            "tutoring_mode",
            "start_date",
            "notes",
            "status",
            "created_at",
        ]
        read_only_fields = ["student_parent", "status"]

    def create(self, validated_data):
        return Booking.objects.create(
            student_parent=self.context["request"].user,
            **validated_data,
        )