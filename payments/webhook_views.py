import stripe

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from bookings.models import Booking
from subscriptions.models import UserSubscription
from earnings.services import create_earning_for_paid_booking


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        booking_id = session.get("metadata", {}).get("booking_id")
        user_subscription_id = session.get("metadata", {}).get("user_subscription_id")

        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.payment_status = "paid"
                booking.payment_reference = session.get("id", "")
                booking.save()
                create_earning_for_paid_booking(booking)
            except Booking.DoesNotExist:
                pass
        if user_subscription_id:
            UserSubscription.objects.filter(id=user_subscription_id).update(
                status="active",
                stripe_customer_id=session.get("customer", ""),
                stripe_subscription_id=session.get("subscription", ""),
            )

    if event["type"] == "customer.subscription.deleted":
        subscription_obj = event["data"]["object"]

        UserSubscription.objects.filter(
            stripe_subscription_id=subscription_obj.get("id")
        ).update(status="cancelled")

    if event["type"] == "customer.subscription.updated":
        subscription_obj = event["data"]["object"]

        UserSubscription.objects.filter(
            stripe_subscription_id=subscription_obj.get("id")
        ).update(
            status=subscription_obj.get("status", "active"),
            current_period_start=timezone.datetime.fromtimestamp(
                subscription_obj.get("current_period_start"),
                tz=timezone.get_current_timezone(),
            ),
            current_period_end=timezone.datetime.fromtimestamp(
                subscription_obj.get("current_period_end"),
                tz=timezone.get_current_timezone(),
            ),
        )

    return HttpResponse(status=200)