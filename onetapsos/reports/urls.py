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
]
