from django.db.models import Sum
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import TutorLedgerEntry, TutorPayout
from .serializers import TutorLedgerEntrySerializer, TutorPayoutSerializer
from notifications.services import create_notification


class TutorEarningsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "tutor":
            return Response({"detail": "Only tutors can view earnings."}, status=403)

        tutor = request.user.tutor_profile
        entries = TutorLedgerEntry.objects.filter(tutor=tutor)

        gross = entries.aggregate(total=Sum("gross_amount"))["total"] or 0
        fees = entries.aggregate(total=Sum("platform_fee"))["total"] or 0
        net = entries.aggregate(total=Sum("net_amount"))["total"] or 0

        paid_out = TutorPayout.objects.filter(
            tutor=tutor,
            status="paid",
        ).aggregate(total=Sum("net_amount"))["total"] or 0

        pending_requested = TutorPayout.objects.filter(
            tutor=tutor,
            status__in=["pending", "processing"],
        ).aggregate(total=Sum("net_amount"))["total"] or 0

        available_for_payout = net - paid_out - pending_requested

        return Response({
            "gross_earnings": gross,
            "platform_fees": fees,
            "net_earnings": net,
            "paid_out": paid_out,
            "pending_requested": pending_requested,
            "pending_payout": available_for_payout,
            "available_for_payout": available_for_payout,
            "total_ledger_entries": entries.count(),
        })


class TutorLedgerListView(ListAPIView):
    serializer_class = TutorLedgerEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "tutor":
            return TutorLedgerEntry.objects.none()

        return TutorLedgerEntry.objects.filter(
            tutor=self.request.user.tutor_profile
        ).order_by("-created_at")


class TutorPayoutListView(ListAPIView):
    serializer_class = TutorPayoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "tutor":
            return TutorPayout.objects.filter(
                tutor=user.tutor_profile
            ).order_by("-created_at")

        if user.role == "admin" or user.is_staff:
            return TutorPayout.objects.all().order_by("-created_at")

        return TutorPayout.objects.none()


class RequestTutorPayoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != "tutor":
            return Response(
                {"detail": "Only tutors can request payouts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        tutor = request.user.tutor_profile

        entries = TutorLedgerEntry.objects.filter(tutor=tutor)
        net = entries.aggregate(total=Sum("net_amount"))["total"] or 0

        paid_out = TutorPayout.objects.filter(
            tutor=tutor,
            status="paid",
        ).aggregate(total=Sum("net_amount"))["total"] or 0

        pending_requested = TutorPayout.objects.filter(
            tutor=tutor,
            status__in=["pending", "processing"],
        ).aggregate(total=Sum("net_amount"))["total"] or 0

        available = net - paid_out - pending_requested

        if available <= 0:
            return Response(
                {"detail": "No available earnings for payout."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payout = TutorPayout.objects.create(
            tutor=tutor,
            amount=available,
            platform_fee=0,
            net_amount=available,
            status="pending",
        )

        create_notification(
            user=request.user,
            notification_type="payment",
            title="Payout requested",
            body=f"Your payout request for ₦{available} has been submitted.",
            action_url="/tutor-earnings",
        )

        return Response(
            TutorPayoutSerializer(payout).data,
            status=status.HTTP_201_CREATED,
        )


class AdminPayoutListView(ListAPIView):
    serializer_class = TutorPayoutSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return TutorPayout.objects.all().order_by("-created_at")


class AdminPayoutDecisionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, payout_id):
        action = request.data.get("action")

        if action not in ["approve", "reject", "processing"]:
            return Response(
                {"detail": "Invalid action. Use approve, reject, or processing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payout = TutorPayout.objects.get(id=payout_id)
        except TutorPayout.DoesNotExist:
            return Response(
                {"detail": "Payout not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if payout.status == "paid":
            return Response(
                {"detail": "This payout has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "approve":
            payout.status = "paid"
            payout.paid_at = timezone.now()
            payout.payout_reference = request.data.get(
                "payout_reference",
                f"PAYOUT-{payout.id}",
            )

            create_notification(
                user=payout.tutor.user,
                notification_type="payment",
                title="Payout approved",
                body=f"Your payout of ₦{payout.net_amount} has been approved.",
                action_url="/tutor-earnings",
            )

        elif action == "processing":
            payout.status = "processing"

            create_notification(
                user=payout.tutor.user,
                notification_type="payment",
                title="Payout processing",
                body=f"Your payout of ₦{payout.net_amount} is now processing.",
                action_url="/tutor-earnings",
            )

        elif action == "reject":
            payout.status = "failed"

            create_notification(
                user=payout.tutor.user,
                notification_type="payment",
                title="Payout rejected",
                body=f"Your payout of ₦{payout.net_amount} was rejected.",
                action_url="/tutor-earnings",
            )

        payout.save()

        return Response(TutorPayoutSerializer(payout).data)