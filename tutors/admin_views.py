from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import TutorProfile
from .serializers import TutorProfileSerializer


class TutorVerificationView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, tutor_id):
        verification_status = request.data.get("verification_status")

        if verification_status not in ["verified", "rejected", "pending"]:
            return Response(
                {"detail": "Invalid verification status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tutor = TutorProfile.objects.get(id=tutor_id)
        except TutorProfile.DoesNotExist:
            return Response(
                {"detail": "Tutor not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        tutor.verification_status = verification_status
        tutor.save()

        return Response(TutorProfileSerializer(tutor).data)