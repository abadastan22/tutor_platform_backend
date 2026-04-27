import uuid
import requests
import stripe

from django.conf import settings


class PaymentError(Exception):
    pass


def initialize_payment(booking, provider=None):
    provider = provider or settings.PAYMENT_PROVIDER

    if provider == "stripe":
        return initialize_stripe_payment(booking)

    if provider == "paystack":
        return initialize_paystack_payment(booking)

    raise PaymentError("Unsupported payment provider.")


def initialize_stripe_payment(booking):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    amount_kobo_or_cents = int(booking.amount * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=booking.student_parent.email,
        line_items=[
            {
                "price_data": {
                    "currency": "ngn",
                    "product_data": {
                        "name": f"Tutoring Session - {booking.subject}",
                    },
                    "unit_amount": amount_kobo_or_cents,
                },
                "quantity": 1,
            }
        ],
        success_url=f"{settings.FRONTEND_URL}/student-dashboard?payment=success",
        cancel_url=f"{settings.FRONTEND_URL}/student-dashboard?payment=cancelled",
        metadata={
            "booking_id": str(booking.id),
        },
    )

    booking.payment_status = "pending"
    booking.payment_reference = session.id
    booking.save()

    return {
        "provider": "stripe",
        "payment_reference": session.id,
        "payment_url": session.url,
        "amount": booking.amount,
        "currency": "NGN",
    }


def initialize_paystack_payment(booking):
    if not settings.PAYSTACK_SECRET_KEY:
        raise PaymentError("PAYSTACK_SECRET_KEY is not configured.")

    reference = f"TUTOR-{uuid.uuid4().hex[:14].upper()}"

    payload = {
        "email": booking.student_parent.email,
        "amount": int(booking.amount * 100),
        "reference": reference,
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
        "metadata": {
            "booking_id": booking.id,
            "student_parent_id": booking.student_parent_id,
            "tutor_id": booking.tutor_id,
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=payload,
        headers=headers,
        timeout=20,
    )

    result = response.json()

    if not result.get("status"):
        raise PaymentError(result.get("message", "Could not initialize Paystack payment."))

    booking.payment_status = "pending"
    booking.payment_reference = reference
    booking.save()

    return {
        "provider": "paystack",
        "payment_reference": reference,
        "payment_url": result["data"]["authorization_url"],
        "access_code": result["data"]["access_code"],
        "amount": booking.amount,
        "currency": "NGN",
    }


def verify_paystack_payment(reference):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers=headers,
        timeout=20,
    )

    result = response.json()

    if not result.get("status"):
        raise PaymentError(result.get("message", "Payment verification failed."))

    return result["data"]