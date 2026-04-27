from django.urls import path
from .views import (
    TutorEarningsSummaryView,
    TutorLedgerListView,
    TutorPayoutListView,
)

urlpatterns = [
    path("earnings/summary/", TutorEarningsSummaryView.as_view()),
    path("earnings/ledger/", TutorLedgerListView.as_view()),
    path("earnings/payouts/", TutorPayoutListView.as_view()),
]