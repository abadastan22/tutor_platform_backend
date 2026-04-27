from rest_framework import generics, permissions
from .models import StudentGoal, ProgressNote
from .serializers import StudentGoalSerializer, ProgressNoteSerializer


class StudentGoalListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudentGoal.objects.filter(
            student_parent=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(student_parent=self.request.user)


class ProgressNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = ProgressNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "tutor":
            return ProgressNote.objects.filter(
                tutor__user=user
            ).order_by("-created_at")

        return ProgressNote.objects.filter(
            student_parent=user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "tutor":
            session = serializer.validated_data.get("session")

            if not session:
                raise PermissionError("Tutor progress notes require a session.")

            serializer.save(
                tutor=user.tutor_profile,
                student_parent=session.student_parent,
            )
        else:
            serializer.save(student_parent=user)