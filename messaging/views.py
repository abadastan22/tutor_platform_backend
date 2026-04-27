from django.contrib.auth import get_user_model
from django.db.models import Max
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Conversation.objects.filter(participants=self.request.user)
            .annotate(last_activity=Max("messages__created_at"))
            .order_by("-updated_at")
        )

    def create(self, request, *args, **kwargs):
        participant_ids = request.data.get("participant_ids", [])
        subject = request.data.get("subject", "")

        if not participant_ids:
            return Response(
                {"detail": "participant_ids is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        participants = User.objects.filter(id__in=participant_ids)

        conversation = Conversation.objects.create(subject=subject)
        conversation.participants.add(request.user, *participants)

        return Response(
            ConversationSerializer(
                conversation,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_id"]

        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=self.request.user,
        ).order_by("created_at")

    def perform_create(self, serializer):
        conversation_id = self.kwargs["conversation_id"]

        conversation = Conversation.objects.get(
            id=conversation_id,
            participants=self.request.user,
        )

        serializer.save(
            conversation=conversation,
            sender=self.request.user,
        )

        conversation.save()


class MarkConversationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conversation_id):
        Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=request.user,
            is_read=False,
        ).exclude(sender=request.user).update(is_read=True)

        return Response({"detail": "Conversation marked as read."})