from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.urls import reverse
from reports.models import EmergencyReport
from .models import Notification

User = get_user_model()

@receiver(post_save, sender=EmergencyReport)
def notify_admins_on_new_report(sender, instance, created, **kwargs):
    if created:
        staff_users = User.objects.filter(is_staff=True)
        for staff in staff_users:
            Notification.objects.create(
                recipient=staff,
                message=f"🚨 New report filed: {instance.report_id} at {instance.location}",
                url=reverse("admin:reports_emergencyreport_change", args=[instance.id])  # ✅ Django admin URL
            )

@receiver(m2m_changed, sender=EmergencyReport.officers_responded.through)
def notify_officers_on_assignment(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for officer_id in pk_set:
            officer = User.objects.get(pk=officer_id)
            if not Notification.objects.filter(
                recipient=officer,
                message__icontains=f"Report {instance.report_id}"
            ).exists():
                Notification.objects.create(
                    recipient=officer,
                    message=f"✅ You’ve been assigned to Report {instance.report_id} ({instance.location})",
                    url=reverse("report_view", kwargs={"report_id": instance.report_id})  # ✅ Officer link
                )
