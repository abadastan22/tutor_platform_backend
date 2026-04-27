from decimal import Decimal

from .models import TutorLedgerEntry


PLATFORM_FEE_RATE = Decimal("0.10")


def create_earning_for_paid_booking(booking):
    if booking.payment_status != "paid":
        return None

    existing = TutorLedgerEntry.objects.filter(
        booking=booking,
        entry_type="earning",
    ).first()

    if existing:
        return existing

    gross = booking.amount
    platform_fee = gross * PLATFORM_FEE_RATE
    net = gross - platform_fee

    return TutorLedgerEntry.objects.create(
        tutor=booking.tutor,
        booking=booking,
        entry_type="earning",
        gross_amount=gross,
        platform_fee=platform_fee,
        net_amount=net,
        description=f"Earning from {booking.subject} booking",
    )