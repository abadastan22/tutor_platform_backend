from django.urls import path
from .views import ReviewCreateView, MyReviewListView, TutorReviewListView

urlpatterns = [
    path("reviews/", ReviewCreateView.as_view()),
    path("reviews/mine/", MyReviewListView.as_view()),
    path("tutors/<int:tutor_id>/reviews/", TutorReviewListView.as_view()),
]