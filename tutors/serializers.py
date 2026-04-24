from rest_framework import serializers
from .models import Subject, TutorProfile


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name"]


class TutorProfileSerializer(serializers.ModelSerializer):
    tutor_name = serializers.SerializerMethodField()
    subjects = SubjectSerializer(many=True, read_only=True)
    subject_ids = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source="subjects",
        many=True,
        write_only=True,
    )

    class Meta:
        model = TutorProfile
        fields = [
            "id",
            "user",
            "tutor_name",
            "bio",
            "subjects",
            "subject_ids",
            "tutoring_mode",
            "city",
            "state",
            "country",
            "hourly_rate",
            "profile_photo",
            "id_document",
            "verification_status",
            "average_rating",
            "total_reviews",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "verification_status",
            "average_rating",
            "total_reviews",
        ]

    def get_tutor_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def create(self, validated_data):
        subjects = validated_data.pop("subjects", [])
        profile = TutorProfile.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )
        profile.subjects.set(subjects)
        return profile