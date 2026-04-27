from .models import Notification


def create_notification(user, notification_type, title, body="", action_url=""):
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        body=body,
        action_url=action_url,
    )