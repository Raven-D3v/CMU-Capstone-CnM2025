from django.contrib import admin
from .models import Caller

@admin.register(Caller)
class CallerAdmin(admin.ModelAdmin):
    list_display = ("caller_id", "full_name", "phone_number", "email", "date_registered")
    search_fields = ("full_name", "phone_number", "email")
    list_filter = ("date_registered",)
    ordering = ("-date_registered",)

