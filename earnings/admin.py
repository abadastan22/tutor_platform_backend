from django.contrib import admin
from .models import TutorLedgerEntry, TutorPayout


@admin.register(TutorLedgerEntry)
class TutorLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "tutor", "entry_type", "gross_amount", "platform_fee", "net_amount", "created_at")
    list_filter = ("entry_type", "created_at")
    search_fields = ("tutor__user__username", "description")


@admin.register(TutorPayout)
class TutorPayoutAdmin(admin.ModelAdmin):
    list_display = ("id", "tutor", "amount", "platform_fee", "net_amount", "status", "created_at", "paid_at")
    list_filter = ("status", "created_at")
    search_fields = ("tutor__user__username", "payout_reference")