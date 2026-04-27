from django.urls import path
from .views import (
    SubscriptionPlanListView,
    MySubscriptionsView,
    CreateStripeSubscriptionCheckoutView,
)

urlpatterns = [
    path("plans/", SubscriptionPlanListView.as_view()),
    path("mine/", MySubscriptionsView.as_view()),
    path("stripe/checkout/", CreateStripeSubscriptionCheckoutView.as_view()),
]