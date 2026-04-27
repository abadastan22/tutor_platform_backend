from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from accounts.models import User
from tutors.models import TutorProfile
from bookings.models import Booking
from reviews.models import Review

from tutors.serializers import TutorProfileSerializer
from bookings.serializers import BookingSerializer
from .serializers import AdminUserSerializer


class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        return Response({
            "total_users": User.objects.count(),
            "total_students": User.objects.filter(role="student_parent").count(),
            "total_tutors": TutorProfile.objects.count(),
            "pending_tutors": TutorProfile.objects.filter(verification_status="pending").count(),
            "verified_tutors": TutorProfile.objects.filter(verification_status="verified").count(),
            "total_bookings": Booking.objects.count(),
            "paid_bookings": Booking.objects.filter(payment_status="paid").count(),
            "total_reviews": Review.objects.count(),
        })


class AdminPendingTutorsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        tutors = TutorProfile.objects.filter(
            verification_status="pending"
        ).order_by("-created_at")

        return Response(TutorProfileSerializer(tutors, many=True).data)


class AdminBookingsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        bookings = Booking.objects.all().order_by("-created_at")[:200]
        return Response(BookingSerializer(bookings, many=True).data)


class AdminUsersView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by("-date_joined")[:300]
        return Response(AdminUserSerializer(users, many=True).data)


class AdminUserStatusView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        is_active = request.data.get("is_active")

        if is_active not in [True, False]:
            return Response(
                {"detail": "is_active must be true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = is_active
        user.save()

        return Response(AdminUserSerializer(user).data)