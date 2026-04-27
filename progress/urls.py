from django.urls import path
from .views import StudentGoalListCreateView, ProgressNoteListCreateView

urlpatterns = [
    path("progress/goals/", StudentGoalListCreateView.as_view()),
    path("progress/notes/", ProgressNoteListCreateView.as_view()),
]