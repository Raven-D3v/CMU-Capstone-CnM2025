from django.contrib import admin
from .models import EmergencyReport

@admin.register(EmergencyReport)
class EmergencyReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'date_time_reported', 'location', 'crime_category', 'status', 'display_officers')
    list_filter = ('crime_category', 'status', 'date_time_reported')
    search_fields = ('report_id', 'location', 'sender')

    # Show M2M properly with a dual list box
    filter_horizontal = ('officers_responded',)  

    def display_officers(self, obj):
        """Display officers in list view."""
        officers = obj.officers_responded.all()
        return ", ".join(str(o) for o in officers) if officers else "None"

    display_officers.short_description = 'Officers Responded'
