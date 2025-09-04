from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Notification
from django.http import JsonResponse

# ---------------- API End POINTS ---------------- #
@login_required
def notifications_json(request):
    latest_notes = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:5]
    data = {
        "unread_count": Notification.objects.filter(recipient=request.user, is_read=False).count(),
        "notifications": [
            {
                "id": n.id,
                "message": n.message,
                "url": n.url or "#",
                "is_read": n.is_read,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for n in latest_notes
        ]
    }
    return JsonResponse(data)



@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by("-created_at")
    return render(request, "notifications/notifications_list.html", {
        "notifications": notifications
    })

@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "ok"})  # no redirect for AJAX

    return redirect(notification.url or "/")
