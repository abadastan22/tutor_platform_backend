from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from earnings.services import create_earning_for_paid_booking

from .models import Booking
from .serializers import BookingSerializer
from payments.services import initialize_payment, verify_paystack_payment, PaymentError


class InitializeBookingPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        provider = request.data.get("provider")

        try:
            booking = Booking.objects.get(
                id=booking_id,
                student_parent=request.user,
            )
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=404)

        if booking.status not in ["accepted", "pending"]:
            return Response(
                {"detail": "Only pending or accepted bookings can be paid."},
                status=400,
            )

        try:
            payment_data = initialize_payment(booking, provider=provider)
        except PaymentError as exc:
            return Response({"detail": str(exc)}, status=400)

        return Response(payment_data)


class VerifyPaystackPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        reference = request.data.get("reference")

        if not reference:
            return Response({"detail": "Payment reference is required."}, status=400)

        try:
            booking = Booking.objects.get(
                payment_reference=reference,
                student_parent=request.user,
            )
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=404)

        try:
            data = verify_paystack_payment(reference)
        except PaymentError as exc:
            return Response({"detail": str(exc)}, status=400)

        if data["status"] == "success":
            booking.payment_status = "paid"
            booking.save()
            create_earning_for_paid_booking(booking)

        return Response(BookingSerializer(booking).data)