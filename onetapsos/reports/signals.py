from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from reports.models import EmergencyReport  # import from reports app
from users.models import DeploymentHistory  # import from users app (adjust if different)
from django.utils import timezone

# When EmergencyReport is saved, update DeploymentHistory status/times
@receiver(post_save, sender=EmergencyReport)
def update_deployment_history_on_report_save(sender, instance, **kwargs):
    # For each officer assigned to this report, update or create DeploymentHistory
    for officer in instance.officers_responded.all():
        deployment, created = DeploymentHistory.objects.get_or_create(
            report=instance,
            police=officer,
            defaults={
                'status': instance.status,
                'date_time_responded': instance.date_time_responded,
                'date_time_resolved': instance.date_time_resolved,
            }
        )
        if not created:
            # Update fields in case report changed
            deployment.status = instance.status
            deployment.date_time_responded = instance.date_time_responded
            deployment.date_time_resolved = instance.date_time_resolved
            deployment.save()

# When officers_responded m2m field changes (add/remove officers)
@receiver(m2m_changed, sender=EmergencyReport.officers_responded.through)
def manage_deployment_on_officers_changed(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        # Add deployment records for newly added officers
        for police_id in pk_set:
            officer = instance.officers_responded.model.objects.get(pk=police_id)
            DeploymentHistory.objects.get_or_create(
                report=instance,
                police=officer,
                defaults={
                    'status': instance.status,
                    'date_time_responded': instance.date_time_responded,
                    'date_time_resolved': instance.date_time_resolved,
                }
            )
    elif action == "post_remove":
        # Optionally delete deployment records for removed officers
        for police_id in pk_set:
            DeploymentHistory.objects.filter(report=instance, police__pk=police_id).delete()
