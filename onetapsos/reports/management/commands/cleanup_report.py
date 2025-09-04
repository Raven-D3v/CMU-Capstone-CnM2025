from django.core.management.base import BaseCommand
from reports.models import EmergencyReport  # adjust if your app is named differently

class Command(BaseCommand):
    help = "Delete expired rejected reports (days_remaining == 0)"

    def handle(self, *args, **kwargs):
        deleted_count = EmergencyReport.delete_expired_reports()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted_count} expired rejected report(s).")
        )
