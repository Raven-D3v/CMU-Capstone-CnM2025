from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()

        latest_notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by("-created_at")[:10]
    else:
        unread_count = 0
        latest_notifications = []

    return {
        "unread_count": unread_count,
        "latest_notifications": latest_notifications,
    }
