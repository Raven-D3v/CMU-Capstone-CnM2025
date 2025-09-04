from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path("reports/json/", views.report_list_json, name="report_list_json"),

    path('archived/', views.archived_reports, name='archived_reports'),
    path('reports/archived/json/', views.archived_reports_json, name='archived_reports_json'),

    path('unclassified/', views.unclassified_reports, name='unclassified_reports'),
    path('view_unclassified/<str:report_id>/', views.view_unclassified_reports, name='view_unclassified'),
    path('reports/unclassified/json/', views.unclassified_reports_json, name='unclassified_reports_json'),


    path('rejected/', views.rejected_reports, name='rejected_reports'),
    path('reports/rejected/json/', views.rejected_reports_json, name='rejected_reports_json'),

    
    path('view/<str:report_id>/', views.report_view, name='report_view'),
    path('edit/<str:report_id>/', views.edit_report, name='edit_report'),
    
    # AJAX Dashboard data endpoints
    path("reports-json/", views.report_list_json, name="report_list_json"),  
    path("reports-stats-json/", views.reports_stats_json, name="reports_stats_json"),  
    path("reports-map-json/", views.reports_map_json, name="reports_map_json"),
    path("status-chart-json/", views.status_chart_json, name="status_chart_json"),
    path('crime-categories-json/', views.crime_categories_json, name='crime_categories_json'),
    path("reports-by-date-json/", views.reports_by_date_json, name="reports_by_date_json"),
    path("reports-by-location-json/", views.reports_by_location_json, name="reports_by_location_json"),
]
