from django.db.models import Sum
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import TutorLedgerEntry, TutorPayout
from .serializers import TutorLedgerEntrySerializer, TutorPayoutSerializer


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

        pending_payout = net - paid_out

        return Response({
            "gross_earnings": gross,
            "platform_fees": fees,
            "net_earnings": net,
            "paid_out": paid_out,
            "pending_payout": pending_payout,
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
        if self.request.user.role != "tutor":
            return TutorPayout.objects.none()

        return TutorPayout.objects.filter(
            tutor=self.request.user.tutor_profile
        ).order_by("-created_at")