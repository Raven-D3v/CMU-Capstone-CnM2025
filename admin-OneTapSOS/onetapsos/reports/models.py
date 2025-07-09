from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class EmergencyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    emergency_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    classification = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default='Unclassified')  # Accepted, Rejected, Archived, etc.
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Report #{self.id} by {self.user}"