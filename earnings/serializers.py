from rest_framework import serializers
from .models import TutorLedgerEntry, TutorPayout


class TutorLedgerEntrySerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()

    class Meta:
        model = TutorLedgerEntry
        fields = [
            "id",
            "entry_type",
            "subject",
            "gross_amount",
            "platform_fee",
            "net_amount",
            "description",
            "created_at",
        ]

    def get_subject(self, obj):
        return obj.booking.subject if obj.booking else ""


class TutorPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorPayout
        fields = [
            "id",
            "amount",
            "platform_fee",
            "net_amount",
            "status",
            "payout_reference",
            "created_at",
            "paid_at",
        ]