from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import Booking
from .serializers import BookingSerializer
from payments.services import initialize_payment, verify_paystack_payment, PaymentError
from earnings.services import create_earning_for_paid_booking

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class InitializeBookingPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        provider = request.data.get("provider", "stripe")

        try:
            booking = Booking.objects.get(
                id=booking_id,
                student_parent=request.user,
            )
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if booking.status not in ["accepted", "pending"]:
            return Response(
                {"detail": "Only pending or accepted bookings can be paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking.payment_status == "paid":
            return Response(
                {"detail": "This booking has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment_data = initialize_payment(booking, provider=provider)
        except PaymentError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(payment_data, status=status.HTTP_200_OK)


class VerifyPaystackPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        reference = request.data.get("reference")

        if not reference:
            return Response(
                {"detail": "Payment reference is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            booking = Booking.objects.get(
                payment_reference=reference,
                student_parent=request.user,
            )
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            data = verify_paystack_payment(reference)
        except PaymentError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if data.get("status") == "success":
            booking.payment_status = "paid"
            booking.save(update_fields=["payment_status"])
            create_earning_for_paid_booking(booking)

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)
    
class VerifyStripeBookingPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(
                id=booking_id,
                student_parent=request.user,
            )
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not booking.payment_reference:
            return Response(
                {"detail": "No Stripe payment reference found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = stripe.checkout.Session.retrieve(booking.payment_reference)
        except Exception as exc:
            return Response(
                {"detail": f"Stripe verification failed: {str(exc)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if session.payment_status == "paid":
            booking.payment_status = "paid"
            booking.save(update_fields=["payment_status"])
            create_earning_for_paid_booking(booking)

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)