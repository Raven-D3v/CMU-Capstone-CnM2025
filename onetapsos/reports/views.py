from django.shortcuts import render, get_object_or_404
from .models import EmergencyReport 

# Create your views here.
def report_list(request):
    # Placeholder view for listing all reports
    return render(request, 'reports/list.html')

def archived_reports(request):
    # Placeholder view for archived reports
    return render(request, 'reports/archived.html')

def unclassified_reports(request):
    # Placeholder view for unclassified reports
    return render(request, 'reports/unclassified.html')

def rejected_reports(request):
    # Placeholder view for rejected reports
    return render(request, 'reports/rejected.html')

def report_view(request, report_id):
    # Placeholder view for viewing a specific report
    report = get_object_or_404(EmergencyReport, id=report_id)
    return render(request, 'reports/view.html', {'report': report})
