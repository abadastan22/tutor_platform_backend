from django.urls import path
from .views import (
    NotificationListView,
    UnreadNotificationCountView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
)

urlpatterns = [
    path("notifications/", NotificationListView.as_view()),
    path("notifications/unread-count/", UnreadNotificationCountView.as_view()),
    path("notifications/<int:notification_id>/read/", MarkNotificationReadView.as_view()),
    path("notifications/read-all/", MarkAllNotificationsReadView.as_view()),
]