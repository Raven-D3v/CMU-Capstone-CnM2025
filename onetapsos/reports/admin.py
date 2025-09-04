from django.contrib import admin
from .models import EmergencyReport

@admin.register(EmergencyReport)
class EmergencyReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'date_time_reported', 'location', 'crime_category', 'status', 'display_officers')
    list_filter = ('crime_category', 'status', 'date_time_reported')
    search_fields = ('report_id', 'location', 'sender')
    readonly_fields = ('display_officers',)

    def display_officers(self, obj):
        """
        Display officers who responded.
        Works for both ManyToMany fields and comma-separated CharFields.
        """
        if hasattr(obj, 'officers_responded') and hasattr(obj.officers_responded, 'all'):
            # ManyToMany case
            officers = obj.officers_responded.all()
            return ", ".join(str(o) for o in officers) if officers else "None"
        elif isinstance(obj.officers_responded, str):
            # Comma-separated string case
            officers = [o.strip() for o in obj.officers_responded.split(',') if o.strip()]
            return ", ".join(officers) if officers else "None"
        return "None"

    display_officers.short_description = 'Officers Responded'
