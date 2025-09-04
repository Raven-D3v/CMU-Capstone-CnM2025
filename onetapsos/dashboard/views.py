from django.shortcuts import render
from django.utils import timezone
from django.db import models
from reports.models import EmergencyReport
from users.models import UserProfile, DeploymentHistory
from django.db.models import Count
from django.db.models.functions import TruncDate
from .utils.location_parser import parse_location
import json


def dashboard_home(request):
    # Get time filter from request (default to 30 days)
    days_filter = int(request.GET.get('days', 30))
    start_date = timezone.now() - timezone.timedelta(days=days_filter)
    filter_type = request.GET.get('filter_type', 'barangay')  # default: barangay
    filter_value = request.GET.get('filter_value', '')        # default: all

    # Base reports (time filter only)
    recent_reports = EmergencyReport.objects.filter(
        date_time_reported__gte=start_date
    )

    # --- Parse all reports upfront ---
    processed_reports = []
    for report in recent_reports:
        loc = parse_location(report.location)
        processed_reports.append({
            "id": report.id,
            "sender_id": report.sender_id,
            "crime_category": report.crime_category,
            "status": report.status,
            "location_raw": report.location,
            **loc,
            "coordinates": report.coordinates,
            "date_time_reported": report.date_time_reported,
        })

    # --- Apply filtering in Python, not in ORM ---
    if filter_value:
        if filter_type == "barangay":
            processed_reports = [r for r in processed_reports if r["subLocality"] == filter_value]
        elif filter_type == "street":
            processed_reports = [r for r in processed_reports if r["thoroughfare"] == filter_value]

    # Prepare crime map data
    crime_map_data = []
    for r in processed_reports:
        coords = r["coordinates"]
        if coords:
            lat = coords.get("lat")
            lng = coords.get("lng")
            if lat and lng:
                crime_map_data.append({
                    "lat": lat,
                    "lng": lng,
                    "intensity": 1.0,
                    "type": r["crime_category"] or "Unclassified",
                    "barangay": r["subLocality"] or "Unknown",
                    "street": r["thoroughfare"] or "Unknown",
                    "location": {
                        "thoroughfare": r["thoroughfare"],
                        "subLocality": r["subLocality"],
                        "locality": r["locality"],
                        "adminArea": r["adminArea"],
                        "countryName": r["countryName"],
                    },
                    "date": r["date_time_reported"].strftime("%Y-%m-%d"),
                    "count": 1,
                })

    # --- Build dropdowns from parsed data ---
    barangays = sorted(set(r["subLocality"] for r in processed_reports if r["subLocality"]))
    streets = sorted(set(r["thoroughfare"] for r in processed_reports if r["thoroughfare"]))

    # Reports per day (for line chart)
    reports_by_date = (
        EmergencyReport.objects
        .annotate(date=TruncDate('date_time_reported'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    context = {
        "now": timezone.now(),

        # Stats cards
        "total_officers": UserProfile.objects.filter(is_staff=True).count(),
        "active_officers": UserProfile.objects.filter(is_staff=True, is_active=True).count(),
        "total_reports": EmergencyReport.objects.count(),
        "active_reports": EmergencyReport.objects.filter(status="active").count(),
        "resolved_reports": EmergencyReport.objects.filter(status="resolved").count(),
        "unclassified_reports": EmergencyReport.objects.filter(status="unclassified").count(),
        "rejected_reports": EmergencyReport.objects.filter(status="rejected").count(),
        "total_callers": EmergencyReport.objects.values('sender').distinct().count(),
        "total_deployments": DeploymentHistory.objects.count(),
        "resolved_deployments": DeploymentHistory.objects.filter(status="resolved").count(),

        # Recent activity (last 7 days)
        "recent_reports": EmergencyReport.objects.filter(
            date_time_reported__gte=timezone.now()-timezone.timedelta(days=7)
        ).count(),
        "recent_deployments": DeploymentHistory.objects.filter(
            date_time_responded__gte=timezone.now()-timezone.timedelta(days=7)
        ).count(),
        "active_officers_recent": UserProfile.objects.filter(
            is_staff=True,
            last_login__gte=timezone.now()-timezone.timedelta(days=7)
        ).count(),

        # Lists
        "latest_reports": EmergencyReport.objects.order_by("-date_time_reported")[:5],
        "top_officers": UserProfile.objects.filter(is_staff=True).order_by("-date_joined")[:5],

        # Chart data
        "crime_categories": EmergencyReport.objects.values("crime_category").annotate(
            count=models.Count("id")
        ),
        "reports_by_date": reports_by_date,

        # Crime map data
        "crime_map_data": json.dumps(crime_map_data),
        "days_filter": days_filter,

        # Filter UI
        "barangays": barangays,
        "streets": streets,
        "filter_type": filter_type,
        "filter_value": filter_value,
    }
    
    # --- Add Status Overview counts ---
    # DB values
    db_to_label = {
        'active': 'Active',
        'resolved': 'Resolved',
        'unclassified': 'Unclassified',
        'rejected': 'Rejected'
        
    }

    # Aggregate counts
    status_order = ['Active', 'Resolved', 'Unclassified', 'Rejected']
    status_data = {label: 0 for label in status_order}
    
    status_counts = EmergencyReport.objects.values('status').annotate(count=Count('id'))

    for entry in status_counts:
        label = db_to_label.get(entry['status'])
        if label:
            status_data[label] = entry['count']


    # Initialize all statuses to 0
    status_data = {label: 0 for label in db_to_label.values()}

    # Fill counts using mapping
    for entry in status_counts:
        label = db_to_label.get(entry['status'])
        if label:
            status_data[label] = entry['count']

    # Add to context
    context['status_data'] = status_data
    print(status_data)
    
    # After building status_data
    context['status_labels'] = json.dumps(list(status_data.keys()))
    context['status_values'] = json.dumps(list(status_data.values()))

    return render(request, "dashboard/dashboard.html", context)

