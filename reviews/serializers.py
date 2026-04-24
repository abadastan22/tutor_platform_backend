from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "booking",
            "reviewer",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["reviewer"]

    def validate(self, attrs):
        request = self.context["request"]
        booking = attrs["booking"]

        if booking.student_parent != request.user:
            raise serializers.ValidationError("You can only review your own booking.")

        return attrs

    def create(self, validated_data):
        return Review.objects.create(
            reviewer=self.context["request"].user,
            **validated_data,
        )