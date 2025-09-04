from datetime import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from .models import EmergencyReport
from users.models import UserProfile
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.contrib import messages
from datetime import timedelta
from collections import defaultdict


# ---------------- Helper Functions ---------------- #
def get_officer_photo_url(user):
    if user.is_authenticated and hasattr(user, 'officer_photo') and user.officer_photo:
        return user.officer_photo.url
    return None


def filter_reports(queryset, query):
    if query:
        queryset = queryset.filter(
            Q(report_id__icontains=query) |
            Q(location__icontains=query)
        )
    return queryset


# ---------------- Ajax ---------------- #
@login_required
def report_list_json(request):
    reports = EmergencyReport.objects.filter(status='active').order_by('-date_time_reported')

    # --- Apply filters from query parameters ---
    q = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date_filter', '').strip()
    location_filter = request.GET.get('location_filter', '').strip()
    crime_filter = request.GET.get('crime_category_filter', '').strip()

    if q:
        reports = reports.filter(
            Q(location__icontains=q) |
            Q(sender__icontains=q) |
            Q(message__icontains=q)
        )

    if date_filter:
        reports = reports.filter(date_time_reported__date=date_filter)

    if location_filter:
        reports = reports.filter(location=location_filter)

    if crime_filter:
        reports = reports.filter(crime_category=crime_filter)

    # --- Build JSON data ---
    data = []
    for r in reports.prefetch_related('officers_responded'):
        data.append({
            "report_id": r.report_id,
            "date_time_reported": r.date_time_reported.strftime("%Y-%m-%d %I:%M %p"),
            "location": r.location,
            "sender": str(r.sender),
            "crime_category": r.get_crime_category_display(),
            "status": r.get_status_display(),
            "date_time_responded": r.date_time_responded.strftime("%Y-%m-%d %I:%M %p") if r.date_time_responded else None,
            "officers_responded": [
                o.get_full_name() if hasattr(o, "get_full_name") else str(o)
                for o in r.officers_responded.all()
            ],
            "date_time_resolved": r.date_time_resolved.strftime("%Y-%m-%d %I:%M %p") if r.date_time_resolved else None,
        })
    return JsonResponse({"reports": data})


@login_required
def archived_reports_json(request):
    # Base queryset: resolved reports
    reports = EmergencyReport.objects.filter(status='resolved').prefetch_related('officers_responded')

    # --- Get filter parameters ---
    query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date_filter', '').strip()
    location_filter = request.GET.get('location_filter', '').strip()
    crime_filter = request.GET.get('crime_category_filter', '').strip()
    status_filter = request.GET.get('status_filter', '').strip()
    sort = request.GET.get('sort', '').strip()

    # --- Apply search ---
    if query:
        reports = reports.filter(
            Q(report_id__icontains=query) |
            Q(location__icontains=query) |
            Q(sender__icontains=query) |
            Q(message__icontains=query)
        )

    # --- Apply filters ---
    if date_filter:
        reports = reports.filter(date_time_reported__date=date_filter)
    if location_filter:
        reports = reports.filter(location=location_filter)
    if crime_filter:
        reports = reports.filter(crime_category=crime_filter)
    if status_filter:
        reports = reports.filter(status=status_filter)

    # --- Sorting ---
    if sort == "date_asc":
        reports = reports.order_by("date_time_reported")
    elif sort == "date_desc":
        reports = reports.order_by("-date_time_reported")
    elif sort == "crime_category":
        reports = reports.order_by("crime_category")
    elif sort == "status":
        reports = reports.order_by("status")
    else:
        reports = reports.order_by("-date_time_reported")

    # --- Build JSON response ---
    data = []
    for r in reports.prefetch_related('officers_responded'):
        data.append({
            "report_id": r.report_id,
            "date_time_reported": r.date_time_reported.strftime("%Y-%m-%d %I:%M %p"),
            "location": r.location,
            "sender": str(r.sender),
            "crime_category": r.get_crime_category_display(),
            "status": r.get_status_display(),
            "date_time_responded": r.date_time_responded.strftime("%Y-%m-%d %I:%M %p") if r.date_time_responded else None,
            "officers_responded": [
                o.get_full_name() if hasattr(o, "get_full_name") else str(o)
                for o in r.officers_responded.all()
            ],
            "date_time_resolved": r.date_time_resolved.strftime("%Y-%m-%d %I:%M %p") if r.date_time_resolved else None,
        })

    return JsonResponse({"reports": data})

@login_required
def rejected_reports_json(request):
    reports = EmergencyReport.objects.filter(status='rejected').order_by('-date_time_reported')

    q = request.GET.get('q','').strip()
    date_filter = request.GET.get('date_filter','').strip()
    location_filter = request.GET.get('location_filter','').strip()

    if q:
        reports = reports.filter(
            Q(report_id__icontains=q) |
            Q(location__icontains=q) |
            Q(sender__icontains=q) |
            Q(message__icontains=q)
        )
    if date_filter:
        reports = reports.filter(date_time_reported__date=date_filter)
    if location_filter:
        reports = reports.filter(location=location_filter)

    data = []
    for r in reports.prefetch_related('officers_responded'):
        data.append({
            'report_id': r.report_id,
            'date_time_reported': r.date_time_reported.strftime("%Y-%m-%d %I:%M %p"),
            'location': r.location,
            'crime_category': r.get_crime_category_display() or 'Unknown',
            'sender': str(r.sender),
            'status': r.get_status_display(),
            'date_time_rejected': r.date_time_rejected.strftime("%Y-%m-%d %I:%M %p") if r.date_time_rejected else None,
            'message': r.message or '--',
            'days_remaining': r.days_remaining,
        })
    return JsonResponse({'reports': data})

@login_required
def unclassified_reports_json(request):
    reports = EmergencyReport.objects.filter(status='unclassified').order_by('-date_time_reported')

    # Get filters
    q = request.GET.get('q','').strip()
    date_filter = request.GET.get('date_filter','').strip()
    location_filter = request.GET.get('location_filter','').strip()

    if q:
        reports = reports.filter(
            Q(report_id__icontains=q) |
            Q(location__icontains=q) |
            Q(sender__icontains=q) |
            Q(message__icontains=q)
        )
    if date_filter:
        reports = reports.filter(date_time_reported__date=date_filter)
    if location_filter:
        reports = reports.filter(location=location_filter)

    # Build JSON response
    data = []
    for r in reports.prefetch_related('officers_responded'):
        data.append({
            'report_id': r.report_id,
            'date_time_reported': r.date_time_reported.strftime("%Y-%m-%d %I:%M %p"),
            'location': r.location,
            'sender': str(r.sender),
            'message': r.message or '--',
        })
    return JsonResponse({'reports': data})



# ---------  Ajax for Dashboard Heat Map   ------------ #
@login_required
def report_json(request):   # new endpoint
    reports = EmergencyReport.objects.order_by("-date_time_reported")[:50]
    data = [
        {
            "id": r.id,
            "type": r.crime_category,
            "date": r.date_time_reported.strftime("%Y-%m-%d %H:%M:%S"),
            "location": r.location,
            "lat": r.coordinates.get("lat") if r.coordinates else None,
            "lng": r.coordinates.get("lng") if r.coordinates else None,
        }
        for r in reports
    ]
    return JsonResponse(data, safe=False)


# Stats Card
def reports_stats_json(request):
    total_reports = EmergencyReport.objects.count()
    active_reports = EmergencyReport.objects.filter(status="active").count()
    unclassified_reports = EmergencyReport.objects.filter(status="unclassified").count()
    resolved_reports = EmergencyReport.objects.filter(status="resolved").count()
    rejected_reports = EmergencyReport.objects.filter(status="rejected").count()

    data = {
        "total_reports": total_reports,
        "active_reports": active_reports,
        "unclassified_reports": unclassified_reports,
        "resolved_reports": resolved_reports,
        "rejected_reports": rejected_reports,
    }
    return JsonResponse(data)


# Heatmap
@login_required
@login_required
def reports_map_json(request):
    # Get filter parameters from query string
    status_filter = request.GET.get("status", "all")
    crime_filter = request.GET.get("crime", "all")

    # Start with reports that have coordinates
    reports = EmergencyReport.objects.exclude(coordinates=None)

    # Apply filters if not 'all'
    if status_filter != "all":
        reports = reports.filter(status__iexact=status_filter)

    if crime_filter != "all":
        reports = reports.filter(crime_category__iexact=crime_filter)

    crime_data = []
    for r in reports:
        lat = r.coordinates.get("lat") if r.coordinates else None
        lng = r.coordinates.get("lng") if r.coordinates else None
        if not lat or not lng:
            continue

        location_parts = r.location.split(",")
        street = location_parts[0].strip() if len(location_parts) > 0 else ""
        barangay = location_parts[1].strip() if len(location_parts) > 1 else ""

        crime_data.append({
            "lat": lat,
            "lng": lng,
            "type": r.crime_category,
            "barangay": barangay,
            "street": street,
            "date": r.date_time_reported.strftime("%Y-%m-%d %I:%M %p"),
            "count": 1,  # each report is separate
            "status": r.status,
        })

    return JsonResponse(crime_data, safe=False)


# Status Chart
@login_required
def status_chart_json(request):
    db_to_label = {
        'active': 'Active',
        'resolved': 'Resolved',
        'unclassified': 'Unclassified',
        'rejected': 'Rejected'
    }
    status_order = ['Active', 'Resolved', 'Unclassified', 'Rejected']
    status_data = {label: 0 for label in status_order}

    status_counts = EmergencyReport.objects.values('status').annotate(count=Count('id'))
    for entry in status_counts:
        label = db_to_label.get(entry['status'])
        if label:
            status_data[label] = entry['count']

    return JsonResponse({
        'labels': status_order,
        'values': [status_data[label] for label in status_order]
    })


# Crime Categories Chart
@login_required
def crime_categories_json(request):
    # Aggregate crime counts
    crime_counts = (
        EmergencyReport.objects
        .values('crime_category')
        .annotate(count=Count('id'))
        .order_by('crime_category')
    )

    # Return JSON
    data = {
        "labels": [item['crime_category'] or "Unclassified" for item in crime_counts],
        "values": [item['count'] for item in crime_counts]
    }
    return JsonResponse(data)


# Date Line Graph
@login_required
def reports_by_date_json(request):
    reports_by_date = (
        EmergencyReport.objects
        .annotate(date=TruncDate('date_time_reported'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    data = {
        "labels": [r['date'].strftime("%Y-%m-%d") for r in reports_by_date],
        "values": [r['count'] for r in reports_by_date]
    }

    return JsonResponse(data)



# Top 5 Barangay Bar Chart
@login_required
def reports_by_location_json(request):
    # Aggregate reports per barangay
    reports_by_barangay = (
        EmergencyReport.objects
        .values('location')  # Or parse into barangay if stored separately
        .annotate(count=Count('id'))
        .order_by('-count')[:5]  # Top 5
    )

    # If location parsing needed
    # For example, if 'Barangay X, Street Y' stored in `location`
    def get_barangay(loc):
        return loc.split(',')[1].strip() if ',' in loc else loc

    labels = [get_barangay(r['location']) for r in reports_by_barangay]
    values = [r['count'] for r in reports_by_barangay]

    return JsonResponse({"labels": labels, "values": values})

# ---------------- Views ---------------- #
@login_required
def report_list(request):
    # ✅ Base queryset: only active reports
    reports = EmergencyReport.objects.filter(status='active').order_by('-date_time_reported')

    # ✅ Search & filters
    query = request.GET.get('q', '')
    date_filter = request.GET.get('date_filter', '')
    location_filter = request.GET.get('location_filter', '')
    crime_filter = request.GET.get('crime_category_filter', '')
    status_filter = request.GET.get('status_filter', '')

    if query:
        reports = reports.filter(
            Q(location__icontains=query) | Q(sender__icontains=query) | Q(message__icontains=query)
        )

    if date_filter:
        reports = reports.filter(date_time_reported__date=date_filter)

    if location_filter:
        reports = reports.filter(location=location_filter)

    if crime_filter:
        reports = reports.filter(crime_category=crime_filter)

    if status_filter:
        reports = reports.filter(status=status_filter)

    # ✅ Distinct values for dropdowns
    locations = EmergencyReport.objects.values_list("location", flat=True).distinct()
    crime_categories = EmergencyReport.CRIME_CATEGORIES  # <-- All defined choices
    statuses = EmergencyReport.STATUS_CHOICES            # <-- All defined choices
    dates = EmergencyReport.objects.dates("date_time_reported", "day").distinct()


    context = {
        "reports": reports,
        "query": query,
        "locations": locations,
        "crime_categories": crime_categories,
        "statuses": statuses,
        "dates": dates,
        "officer_photo_url": get_officer_photo_url(request.user),
    }
    return render(request, "reports/list.html", context)



@login_required
def archived_reports(request):
    # Base queryset: resolved reports
    reports = EmergencyReport.objects.filter(status='resolved').prefetch_related('officers_responded')

    # --- Get filter parameters ---
    query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date_filter', '').strip()
    location_filter = request.GET.get('location_filter', '').strip()
    crime_filter = request.GET.get('crime_category_filter', '').strip()
    status_filter = request.GET.get('status_filter', '').strip()
    sort = request.GET.get('sort', '').strip()

    # --- Apply search ---
    if query:
        reports = reports.filter(
            Q(report_id__icontains=query) |
            Q(location__icontains=query) |
            Q(sender__icontains=query) |
            Q(message__icontains=query)
        )

    # --- Apply filters ---
    if date_filter:
        reports = reports.filter(date_time_reported__date=date_filter)

    if location_filter:
        reports = reports.filter(location=location_filter)

    if crime_filter:
        reports = reports.filter(crime_category=crime_filter)

    if status_filter:
        reports = reports.filter(status=status_filter)

    # --- Sorting ---
    if sort == "date_asc":
        reports = reports.order_by("date_time_reported")
    elif sort == "date_desc":
        reports = reports.order_by("-date_time_reported")
    elif sort == "crime_category":
        reports = reports.order_by("crime_category")
    elif sort == "status":
        reports = reports.order_by("status")
    else:
        reports = reports.order_by("-date_time_reported")  # default

    # --- Dropdown values ---
    dates = reports.dates("date_time_reported", "day").distinct()
    locations = reports.values_list("location", flat=True).distinct()
    crime_categories = EmergencyReport.CRIME_CATEGORIES
    statuses = EmergencyReport.STATUS_CHOICES

    context = {
        "reports": reports,
        "query": query,
        "dates": dates,
        "locations": locations,
        "crime_categories": crime_categories,
        "statuses": statuses,
        "sort": sort,
        "officer_photo_url": get_officer_photo_url(request.user),
    }
    return render(request, "reports/archived.html", context)





@login_required
def unclassified_reports(request):
    # Base queryset: unclassified reports
    reports = EmergencyReport.objects.filter(status='unclassified').order_by('-date_time_reported')

    # Get filter parameters
    query = request.GET.get('q', '')
    date_filter = request.GET.get('date_filter', '')
    location_filter = request.GET.get('location_filter', '')

    # Apply search filter
    if query:
        reports = reports.filter(
            Q(location__icontains=query) |
            Q(sender__icontains=query) |
            Q(message__icontains=query)
        )

    # Apply date filter
    if date_filter:
        reports = reports.filter(date_time_reported__date=date_filter)

    # Apply location filter
    if location_filter:
        reports = reports.filter(location=location_filter)

    # Distinct values for dropdowns
    dates = EmergencyReport.objects.filter(status='unclassified').dates('date_time_reported', 'day').distinct()
    locations = EmergencyReport.objects.filter(status='unclassified').values_list('location', flat=True).distinct()

    context = {
        'reports': reports,
        'query': query,
        'dates': dates,
        'locations': locations,
        'officer_photo_url': get_officer_photo_url(request.user),
    }

    return render(request, 'reports/unclassified.html', context)



@login_required
def view_unclassified_reports(request, report_id):
    report = get_object_or_404(EmergencyReport, report_id=report_id, status='unclassified')
    officer_photo_url = get_officer_photo_url(request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            # Grab selected crime category
            crime_category = request.POST.get("crime_category")
            if not crime_category or crime_category not in dict(EmergencyReport.CRIME_CATEGORIES):
                return render(request, "reports/view_unclassified.html", {
                    "report": report,
                    "crime_choices": EmergencyReport.CRIME_CATEGORIES,
                    "error": "Please select a valid crime category.",
                    "officer_photo_url": officer_photo_url,
                })

            report.crime_category = crime_category
            report.status = "active"

            try:
                report.save()
            except ValueError as e:
                return render(request, "reports/view_unclassified.html", {
                    "report": report,
                    "crime_choices": EmergencyReport.CRIME_CATEGORIES,
                    "error": str(e),
                    "officer_photo_url": officer_photo_url,
                })

            return redirect('unclassified_reports')

        elif action == "reject":
            report.status = "rejected"
            report.save()
            return redirect('unclassified_reports')

    context = {
        "report": report,
        "crime_choices": EmergencyReport.CRIME_CATEGORIES,
        "officer_photo_url": officer_photo_url,
    }
    return render(request, "reports/view_unclassified.html", context)





@login_required
def rejected_reports(request):
    # Base queryset: rejected reports only
    reports = EmergencyReport.objects.filter(status='rejected').order_by('-date_time_reported')

    # --- Get filter parameters ---
    query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date_filter', '').strip()
    location_filter = request.GET.get('location_filter', '').strip()

    # --- Apply filters ---
    if query:
        reports = reports.filter(
            Q(report_id__icontains=query) |
            Q(location__icontains=query) |
            Q(sender__icontains=query) |
            Q(message__icontains=query)
        )

    if date_filter:
        reports = reports.filter(date_time_reported__date=date_filter)

    if location_filter:
        reports = reports.filter(location=location_filter)

    # --- Distinct values for dropdowns ---
    dates = EmergencyReport.objects.filter(status='rejected').dates('date_time_reported', 'day').distinct()
    locations = EmergencyReport.objects.filter(status='rejected').values_list('location', flat=True).distinct()

    context = {
        'reports': reports,
        'query': query,
        'dates': dates,
        'locations': locations,
        'officer_photo_url': get_officer_photo_url(request.user),
    }
    return render(request, 'reports/rejected.html', context)




@login_required
def report_view(request, report_id):
    report = get_object_or_404(
        EmergencyReport,
        report_id=report_id,
        status__in=['active', 'rejected','resolved']  # <- include rejected reports
    )

    context = {
        'report': report,
        'officer_photo_url': get_officer_photo_url(request.user),
        'officers_responded': report.officers_responded.all(),
    }

    return render(request, 'reports/view.html', context)



@login_required
def edit_report(request, report_id):
    report = get_object_or_404(EmergencyReport, report_id=report_id)
    officer_choices = UserProfile.objects.filter(is_staff=False, is_superuser=False)

    if request.method == "POST":
        # Update editable fields
        report.crime_category = request.POST.get("crime_category")
        report.status = request.POST.get("status")
        report.rejection_reason = request.POST.get("rejection_reason", report.rejection_reason)

        date_responded = request.POST.get("date_responded")
        date_resolved = request.POST.get("date_resolved")

        report.date_time_responded = parse_datetime(date_responded) if date_responded else None
        report.date_time_resolved = parse_datetime(date_resolved) if date_resolved else None

        selected_officers = request.POST.getlist("officers")
        report.officers_responded.set(UserProfile.objects.filter(id__in=selected_officers))

        report.save()
        # Refresh to ensure dynamic fields (e.g., date_time_rejected) are populated
        report.refresh_from_db()
        return redirect('report_list')

    # Calculate days remaining if report is rejected
    days_remaining = report.days_remaining if report.status == "rejected" else None

    context = {
        'report': report,
        'crime_choices': EmergencyReport.CRIME_CATEGORIES,
        'status_choices': EmergencyReport.STATUS_CHOICES,
        'officer_choices': officer_choices,
        'days_remaining': days_remaining,  # pass explicitly to template
    }
    return render(request, 'reports/edit_report.html', context)





