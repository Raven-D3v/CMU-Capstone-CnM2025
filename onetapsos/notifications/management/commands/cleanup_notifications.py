from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from notifications.models import Notification

class Command(BaseCommand):
    help = "Delete notifications older than 7 days"

    def handle(self, *args, **kwargs):
        cutoff_date = timezone.now() - timedelta(days=7)
        deleted_count, _ = Notification.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted_count} old notification(s).")
        )
