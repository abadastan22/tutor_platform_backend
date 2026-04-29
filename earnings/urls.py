from django.urls import path
from .views import (
    TutorEarningsSummaryView,
    TutorLedgerListView,
    TutorPayoutListView,
    RequestTutorPayoutView,
    AdminPayoutListView,
    AdminPayoutDecisionView,
)

urlpatterns = [
    path("earnings/summary/", TutorEarningsSummaryView.as_view()),
    path("earnings/ledger/", TutorLedgerListView.as_view()),
    path("earnings/payouts/", TutorPayoutListView.as_view()),
    path("earnings/payouts/request/", RequestTutorPayoutView.as_view()),

    path("admin/earnings/payouts/", AdminPayoutListView.as_view()),
    path(
        "admin/earnings/payouts/<int:payout_id>/decision/",
        AdminPayoutDecisionView.as_view(),
    ),
]