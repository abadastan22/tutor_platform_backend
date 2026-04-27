from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    tutor_name = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "booking",
            "reviewer",
            "tutor_name",
            "subject",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["reviewer"]

    def get_tutor_name(self, obj):
        return obj.booking.tutor.user.get_full_name() or obj.booking.tutor.user.username

    def get_subject(self, obj):
        return obj.booking.subject

    def create(self, validated_data):
        request = self.context["request"]

        review = Review(
            reviewer=request.user,
            **validated_data,
        )

        review.full_clean()
        review.save()

        return review