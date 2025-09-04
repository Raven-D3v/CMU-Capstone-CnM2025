from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.police_id}: {self.message[:50]}"

    @classmethod
    def delete_old_notifications(cls, days=7):
        """
        Deletes all notifications older than `days`.
        Default is 7 days.
        """
        cutoff = timezone.now() - timedelta(days=days)
        old_qs = cls.objects.filter(created_at__lt=cutoff)
        count = old_qs.count()
        old_qs.delete()
        return count
