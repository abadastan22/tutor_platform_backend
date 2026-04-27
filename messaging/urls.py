from django.urls import path
from .views import (
    ConversationListCreateView,
    MessageListCreateView,
    MarkConversationReadView,
)

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view()),
    path("conversations/<int:conversation_id>/messages/", MessageListCreateView.as_view()),
    path("conversations/<int:conversation_id>/read/", MarkConversationReadView.as_view()),
]