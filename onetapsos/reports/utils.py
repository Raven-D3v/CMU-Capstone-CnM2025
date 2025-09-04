#A python file made for Helpers
from django.db.models import Q

def filter_reports_date(reports, query, date_filter=None, location_filter=None, crime_category_filter=None):
    if query:
        reports = reports.filter(
            Q(report_id__icontains=query) |
            Q(location__icontains=query) |
            Q(sender__icontains=query)
        )
    if date_filter:
        reports = reports.filter(date_time_reported__date=date_filter)
    if location_filter:
        reports = reports.filter(location__icontains=location_filter)
    if crime_category_filter:
        reports = reports.filter(crime_category=crime_category_filter)

    return reports

