from django.urls import path
from .views import SubjectListView, TutorListView, TutorCreateView, TutorDetailView
from .admin_views import TutorVerificationView

urlpatterns = [
    path("subjects/", SubjectListView.as_view()),
    path("tutors/", TutorListView.as_view()),
    path("tutors/register/", TutorCreateView.as_view()),
    path("tutors/<int:pk>/", TutorDetailView.as_view()),
    path("admin/tutors/<int:tutor_id>/verify/", TutorVerificationView.as_view()),
]