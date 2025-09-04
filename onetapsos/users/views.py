from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.contrib import messages
from .forms import RegistrationForm 
from .models import UserProfile, DeploymentHistory
from callers.models import Caller
from reports.models import EmergencyReport
from django.db.models import OuterRef, Subquery, Q

# Login View

def login_view(request):
    if request.method == "POST":
        police_id = request.POST.get("police_id")
        password = request.POST.get("password")

        # First, get the user manually
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(police_id=police_id)
        except User.DoesNotExist:
            user = None

        # Check password manually if user exists
        if user is not None and user.check_password(password):
            if user.is_active:
                login(request, user)
                messages.success(request, "Login Successful!")
                return redirect('dashboard')
            else:
                messages.warning(request, "Your account is not yet activated. Please wait for verification.")
        else:
            messages.error(request, "Invalid Police ID or Password.")

    return render(request, 'users/login.html')

@login_required
def officer_logout(request):
    logout(request)
    messages.success(request, "You have been logout")
    return redirect('login')


# Register View
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')  # replace with your actual login URL name
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

#Dashboard View
@login_required
def dashboard_view(request):
    return render(request, 'users/dashboard.html')

# List of officers
@login_required
def officer_list(request):
    # Subquery for last deployment
    latest_deployment = (
        DeploymentHistory.objects
        .filter(police_id=OuterRef("police_id"))
        .order_by("-date_time_responded", "-date_time_resolved", "-id")
    )

    users = (
        UserProfile.objects
        .filter(is_staff=False, is_superuser=False)
        .annotate(
            last_status=Subquery(latest_deployment.values("status")[:1]),
            last_report_id=Subquery(latest_deployment.values("report__report_id")[:1]),
            last_responded=Subquery(latest_deployment.values("date_time_responded")[:1]),
            last_resolved=Subquery(latest_deployment.values("date_time_resolved")[:1]),
        )
    )

    # 🔍 Search
    q = request.GET.get("q")
    if q:
        users = users.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(police_id__icontains=q) |
            Q(designation__icontains=q) |
            Q(area_vicinity__icontains=q)
        )

    # 🎖️ Rank filter
    rank = request.GET.get("rank")
    if rank:
        users = users.filter(rank=rank)

    # 🏷️ Designation filter
    designation = request.GET.get("designation")
    if designation:
        users = users.filter(designation=designation)

    # 📍 Area filter
    area = request.GET.get("area")
    if area:
        users = users.filter(area_vicinity=area)

    # ✅ Status filter (deployment status)
    status = request.GET.get("status")
    if status:
        users = users.filter(last_status=status)

    users = users.order_by("rank", "last_name")

    # Distinct dropdown values
    ranks = UserProfile.objects.values_list("rank", flat=True).distinct()
    designations = (
    UserProfile.objects
    .exclude(designation__isnull=True)
    .exclude(designation="")
    .values_list("designation", flat=True)
    .distinct()
)
    areas = (
    UserProfile.objects
    .exclude(area_vicinity__isnull=True)
    .exclude(area_vicinity="")
    .values_list("area_vicinity", flat=True)
    .distinct()
)
    statuses = DeploymentHistory.objects.values_list("status", flat=True).distinct()

    return render(request, "users/officers_list.html", {
        "users": users,
        "ranks": ranks,
        "designations": designations,
        "areas": areas,
        "statuses": statuses,
        "filters": request.GET,
    })


# View a Specific Officer
@login_required
def officer_view(request, user_id):
    if request.user.id != user_id:
        return HttpResponseForbidden("You can only view your own profile.")

    user = get_object_or_404(UserProfile, id=user_id)

    # Fix here: use 'report__date_time_reported' instead of 'date_time_reported'
    deployments = DeploymentHistory.objects.filter(police=user).order_by('-report__date_time_reported')

    return render(request, 'users/officers_view.html', {
        'user': user,
        'deployments': deployments
    })



@login_required
def callers_list(request):
    # Subquery for the latest report of each caller
    latest_report = EmergencyReport.objects.filter(
        sender=OuterRef("pk")
    ).order_by("-date_time_reported")

    callers = Caller.objects.annotate(
        last_report_id=Subquery(latest_report.values("report_id")[:1]),
        last_report_status=Subquery(latest_report.values("status")[:1]),
        last_report_category=Subquery(latest_report.values("crime_category")[:1]),
        last_report_date=Subquery(latest_report.values("date_time_reported")[:1]),
        last_report_location=Subquery(latest_report.values("location")[:1]),
    )

    return render(request, "users/callers_list.html", {"callers": callers})

@login_required
def callers_view(request, caller_id):
    caller = get_object_or_404(Caller, caller_id=caller_id)
    reports = caller.reports.all().order_by('-date_time_reported')
    return render(request, "users/callers_view.html", {
        "caller": caller,
        "reports": reports
    })