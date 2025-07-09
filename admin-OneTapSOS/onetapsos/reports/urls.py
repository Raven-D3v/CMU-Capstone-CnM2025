from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('archived/', views.archived_reports, name='archived_reports'),
    path('unclassified/', views.unclassified_reports, name='unclassified_reports'),
    path('rejected/', views.rejected_reports, name='rejected_reports'),
    path('view/<int:report_id>/', views.report_view, name='report_view'),
]
