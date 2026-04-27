import stripe

from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SubscriptionPlan, UserSubscription
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer


class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class MySubscriptionsView(generics.ListAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user).order_by("-created_at")


class CreateStripeSubscriptionCheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan_id")

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "Plan not found."}, status=404)

        if not plan.stripe_price_id:
            return Response(
                {"detail": "Plan does not have a Stripe price configured."},
                status=400,
            )

        stripe.api_key = settings.STRIPE_SECRET_KEY

        subscription = UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            tutor=plan.tutor,
            status="incomplete",
        )

        session = stripe.checkout.Session.create(
            mode="subscription",
            customer_email=request.user.email,
            line_items=[
                {
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                }
            ],
            success_url=f"{settings.FRONTEND_URL}/subscription?status=success",
            cancel_url=f"{settings.FRONTEND_URL}/subscription?status=cancelled",
            metadata={
                "user_subscription_id": str(subscription.id),
                "user_id": str(request.user.id),
                "plan_id": str(plan.id),
            },
        )

        return Response({
            "checkout_url": session.url,
            "session_id": session.id,
            "subscription_id": subscription.id,
        })