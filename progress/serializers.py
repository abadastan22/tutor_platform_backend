from rest_framework import serializers
from .models import StudentGoal, ProgressNote


class StudentGoalSerializer(serializers.ModelSerializer):
    tutor_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentGoal
        fields = [
            "id",
            "student_parent",
            "tutor",
            "tutor_name",
            "subject",
            "subject_name",
            "title",
            "description",
            "target_date",
            "progress_percent",
            "status",
            "created_at",
        ]
        read_only_fields = ["student_parent"]

    def get_tutor_name(self, obj):
        if not obj.tutor:
            return ""
        return obj.tutor.user.get_full_name() or obj.tutor.user.username

    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else ""


class ProgressNoteSerializer(serializers.ModelSerializer):
    tutor_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = ProgressNote
        fields = [
            "id",
            "student_parent",
            "student_name",
            "tutor",
            "tutor_name",
            "session",
            "subject",
            "note",
            "homework",
            "score",
            "created_at",
        ]
        read_only_fields = ["student_parent"]

    def get_tutor_name(self, obj):
        return obj.tutor.user.get_full_name() or obj.tutor.user.username

    def get_student_name(self, obj):
        return obj.student_parent.get_full_name() or obj.student_parent.username