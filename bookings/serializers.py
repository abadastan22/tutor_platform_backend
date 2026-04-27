from rest_framework import serializers
from .models import Booking, TutorAvailability
from .models import ScheduledSession


class TutorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorAvailability
        fields = [
            "id",
            "tutor",
            "day_of_week",
            "start_time",
            "end_time",
            "is_active",
        ]
        read_only_fields = ["tutor"]


class BookingSerializer(serializers.ModelSerializer):
    tutor_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "student_parent",
            "tutor",
            "tutor_name",
            "subject",
            "tutoring_mode",
            "start_date",
            "start_time",
            "duration_minutes",
            "location_address",
            "meeting_link",
            "notes",
            "status",
            "payment_status",
            "amount",
            "payment_reference",
            "created_at",
        ]
        read_only_fields = [
            "student_parent",
            "status",
            "payment_status",
            "payment_reference",
            "meeting_link",
        ]

    def get_tutor_name(self, obj):
        return obj.tutor.user.get_full_name() or obj.tutor.user.username

    def create(self, validated_data):
        tutor = validated_data["tutor"]
        duration_minutes = validated_data.get("duration_minutes", 60)

        amount = tutor.hourly_rate * duration_minutes / 60

        return Booking.objects.create(
            student_parent=self.context["request"].user,
            amount=amount,
            **validated_data,
        )
        
class ScheduledSessionSerializer(serializers.ModelSerializer):
    tutor_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledSession
        fields = [
            "id",
            "booking",
            "tutor",
            "tutor_name",
            "student_parent",
            "student_name",
            "subject",
            "session_date",
            "start_time",
            "end_time",
            "meeting_link",
            "is_completed",
            "created_at",
        ]

    def get_tutor_name(self, obj):
        return obj.tutor.user.get_full_name() or obj.tutor.user.username

    def get_student_name(self, obj):
        return obj.student_parent.get_full_name() or obj.student_parent.username

    def get_subject(self, obj):
        return obj.booking.subject