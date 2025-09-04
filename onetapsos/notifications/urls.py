from django.urls import path
from . import views

urlpatterns = [
    path("", views.notifications_list, name="notifications_list"),
    path("<int:pk>/read/", views.mark_as_read, name="mark_as_read"),
    path("mark/<int:pk>/", views.mark_as_read, name="mark_as_read"),
    path("json/", views.notifications_json, name="notifications_json"),  # <- add this
]

