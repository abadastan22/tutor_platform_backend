from django.urls import path
from .views import SubjectListView, TutorListView, TutorCreateView, TutorDetailView

urlpatterns = [
    path("subjects/", SubjectListView.as_view()),
    path("tutors/", TutorListView.as_view()),
    path("tutors/register/", TutorCreateView.as_view()),
    path("tutors/<int:pk>/", TutorDetailView.as_view()),
]