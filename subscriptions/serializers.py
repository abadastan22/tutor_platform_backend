from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "description",
            "tutor",
            "price",
            "currency",
            "interval",
            "sessions_per_interval",
            "stripe_price_id",
            "is_active",
        ]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_detail = SubscriptionPlanSerializer(source="plan", read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            "id",
            "user",
            "plan",
            "plan_detail",
            "tutor",
            "status",
            "stripe_customer_id",
            "stripe_subscription_id",
            "current_period_start",
            "current_period_end",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "status",
            "stripe_customer_id",
            "stripe_subscription_id",
            "current_period_start",
            "current_period_end",
        ]