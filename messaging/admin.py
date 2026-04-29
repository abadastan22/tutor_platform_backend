from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "created_at", "updated_at")
    search_fields = ("subject",)
    filter_horizontal = ("participants",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("sender__username", "body")