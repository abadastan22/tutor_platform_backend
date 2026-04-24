from django.urls import path
from .views import ReviewCreateView, TutorReviewListView

urlpatterns = [
    path("reviews/", ReviewCreateView.as_view()),
    path("tutors/<int:tutor_id>/reviews/", TutorReviewListView.as_view()),
]