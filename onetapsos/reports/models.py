from datetime import date, timedelta
from django.db import models, transaction
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings

class EmergencyReport(models.Model):
    report_id = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(
            r'^RPT-\d{4}-\d{4}$',
            'Report ID must be in format RPT-YYYY-0000'
        )]
    )
    date_time_reported = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=255)
    sender = models.ForeignKey(
        "callers.Caller",
        on_delete=models.CASCADE,
        related_name="reports"
    )
    message = models.TextField(blank=True, null=True)

    CRIME_CATEGORIES = [
        ('assault', 'Assault'),
        ('sexual_assault', 'Sexual Assault'),
        ('robbery', 'Robbery'),
        ('other', 'Other'),
    ]
    crime_category = models.CharField(max_length=50, choices=CRIME_CATEGORIES, blank=True, null=True)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('unclassified', 'Unclassified'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    rejection_reason = models.TextField(blank=True, null=True)

    date_time_responded = models.DateTimeField(null=True, blank=True)
    officers_responded = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='reports_responded_to',
        help_text='Officers who responded to this report'
    )
    date_time_resolved = models.DateTimeField(null=True, blank=True)
    date_time_rejected = models.DateTimeField(null=True, blank=True)

    # Number of days after rejection until it expires
    REJECTION_EXPIRATION_DAYS = 7

    ALLOWED_TRANSITIONS = {
        'active': ['resolved', 'rejected', 'unclassified'],
        'unclassified': ['resolved', 'rejected'],
        'resolved': [],
        'rejected': []
    }

    class Meta:
        ordering = ['-date_time_reported']

    def save(self, *args, **kwargs):
        # Automatically set rejection time
        if self.status == 'rejected' and not self.date_time_rejected:
            self.date_time_rejected = timezone.now()

        # Enforce allowed status transitions
        if self.pk:
            old_status = EmergencyReport.objects.get(pk=self.pk).status
            if old_status == 'unclassified' and self.status == 'active' and self.crime_category:
                pass  # allowed
            elif self.status != old_status and self.status not in self.ALLOWED_TRANSITIONS.get(old_status, []):
                raise ValueError(f"Invalid status change from {old_status} to {self.status}")

        # Generate report_id if not set
        if not self.report_id:
            current_year = date.today().year
            with transaction.atomic():
                last_report = (
                    EmergencyReport.objects
                    .select_for_update()
                    .filter(report_id__startswith=f"RPT-{current_year}-")
                    .order_by('-report_id')
                    .first()
                )

                last_number = 0
                if last_report:
                    try:
                        last_number = int(last_report.report_id.split('-')[-1])
                    except ValueError:
                        pass

                self.report_id = f"RPT-{current_year}-{last_number + 1:04d}"

        super().save(*args, **kwargs)

    @property
    def days_remaining(self):
        """Returns number of days left before a rejected report expires."""
        if self.status == 'rejected' and self.date_time_rejected:
            expiration_date = self.date_time_rejected.date() + timedelta(days=self.REJECTION_EXPIRATION_DAYS)
            remaining = expiration_date - timezone.now().date()
            return max(remaining.days, 0)
        return None

    @classmethod
    def delete_expired_reports(cls):
        """
        Deletes all rejected reports whose days_remaining == 0.
        Uses the days_remaining property directly.
        """
        expired = []
        for report in cls.objects.filter(status='rejected', date_time_rejected__isnull=False):
            if report.days_remaining == 0:
                expired.append(report)
                report.delete()

        return len(expired)

