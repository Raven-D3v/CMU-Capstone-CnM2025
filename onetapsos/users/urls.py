from django.urls import include, path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.officer_logout, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('list/', views.officer_list, name='officer_list'),
    path('view/<int:user_id>/', views.officer_view, name='officer_view'),
    path('callerslist/', views.callers_list, name='callers_list'),
    path('callersview/<int:caller_id>/', views.callers_view, name='callers_view'),
    path("notifications/", include("notifications.urls")),
    
]

