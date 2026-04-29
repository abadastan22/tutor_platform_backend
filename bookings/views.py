from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
from notifications.services import create_notification

from .models import Booking, TutorAvailability, ScheduledSession
from .serializers import (
    BookingSerializer,
    TutorAvailabilitySerializer,
    ScheduledSessionSerializer,
)


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "tutor":
            return Booking.objects.filter(tutor__user=user).order_by("-created_at")

        return Booking.objects.filter(student_parent=user).order_by("-created_at")


class TutorAvailabilityListCreateView(generics.ListCreateAPIView):
    serializer_class = TutorAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        tutor_id = self.request.query_params.get("tutor")

        queryset = TutorAvailability.objects.filter(is_active=True)

        # Public lookup for booking page:
        # GET /api/availability/?tutor=1
        if tutor_id:
            return queryset.filter(tutor_id=tutor_id).order_by(
                "day_of_week",
                "start_time",
            )

        # Tutor dashboard lookup:
        # GET /api/availability/
        if self.request.user.is_authenticated and self.request.user.role == "tutor":
            return TutorAvailability.objects.filter(
                tutor__user=self.request.user
            ).order_by("day_of_week", "start_time")

        return TutorAvailability.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_authenticated:
            raise permissions.PermissionDenied("Authentication required.")

        if user.role != "tutor":
            raise permissions.PermissionDenied("Only tutors can add availability.")

        serializer.save(tutor=user.tutor_profile)


class BookingDecisionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        action = request.data.get("action")

        try:
            booking = Booking.objects.get(id=booking_id, tutor__user=request.user)
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if action == "accept":
            booking.status = "accepted"

        if booking.tutoring_mode == "online" and not booking.meeting_link:
            booking.meeting_link = f"https://meet.google.com/demo-{booking.id}"

        if booking.start_time:
            start_dt = datetime.combine(booking.start_date, booking.start_time)
            end_dt = start_dt + timedelta(minutes=booking.duration_minutes)

            ScheduledSession.objects.get_or_create(
                booking=booking,
                tutor=booking.tutor,
                student_parent=booking.student_parent,
                session_date=booking.start_date,
                start_time=booking.start_time,
                defaults={
                    "end_time": end_dt.time(),
                    "meeting_link": booking.meeting_link,
                },
            )

        create_notification(
            user=booking.student_parent,
            notification_type="booking",
            title="Booking accepted",
            body=f"Your booking for {booking.subject} has been accepted.",
            action_url="/student-dashboard",
        )
    
class ScheduledSessionListView(generics.ListAPIView):
    serializer_class = ScheduledSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "tutor":
            return ScheduledSession.objects.filter(tutor__user=user)

        return ScheduledSession.objects.filter(student_parent=user)
    

class CompleteBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        user = request.user

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_tutor_owner = user.role == "tutor" and booking.tutor.user == user
        is_admin = user.role == "admin" or user.is_staff

        if not is_tutor_owner and not is_admin:
            return Response(
                {"detail": "You do not have permission to complete this booking."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.status != "accepted":
            return Response(
                {"detail": "Only accepted bookings can be marked as completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = "completed"
        booking.save(update_fields=["status"])

        booking.sessions.update(is_completed=True)

        create_notification(
            user=booking.student_parent,
            notification_type="booking",
            title="Session completed",
            body=f"Your {booking.subject} session has been marked as completed. You may review this tutor after 30 days.",
            action_url="/student-dashboard",
        )

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)