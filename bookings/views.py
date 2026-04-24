from rest_framework import generics, permissions
from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "tutor":
            return Booking.objects.filter(tutor__user=user)

        return Booking.objects.filter(student_parent=user)

    def perform_create(self, serializer):
        serializer.save(student_parent=self.request.user)