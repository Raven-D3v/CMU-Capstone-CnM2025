from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import UserProfile, DeploymentHistory
from django.utils.translation import gettext_lazy as _

@admin.register(UserProfile)
class CustomUserAdmin(UserAdmin):
    model = UserProfile
    list_display = (
        'police_id', 'email', 'rank', 'designation', 'area_vicinity',
        'first_name', 'last_name', 'is_active', 'photo_thumbnail'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'rank', 'designation', 'area_vicinity', 'groups')
    search_fields = ('police_id', 'email', 'first_name', 'last_name', 'designation', 'area_vicinity')

    readonly_fields = ('date_joined', 'last_login', 'photo_preview')

    fieldsets = (
        (None, {'fields': ('police_id', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number',
                'rank', 'designation', 'area_vicinity',
                'officer_photo', 'photo_preview'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'police_id', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'phone_number', 'rank',
                'designation', 'area_vicinity',
                'officer_photo', 'is_active', 'is_staff', 'is_superuser', 'groups'
            )}
        ),
    )

    ordering = ('police_id',)

    def photo_thumbnail(self, obj):
        if obj.officer_photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%;" />',
                obj.officer_photo.url
            )
        return "No Photo"
    photo_thumbnail.short_description = 'Photo'

    def photo_preview(self, obj):
        if obj.officer_photo:
            return format_html('<img src="{}" width="150" />', obj.officer_photo.url)
        return "No Photo"
    photo_preview.short_description = 'Preview'



@admin.register(DeploymentHistory)
class DeploymentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'get_report_id', 'get_report_location', 'get_report_crime_category',
        'get_report_sender', 'status', 'police', 'date_time_responded', 'date_time_resolved'
    )
    list_filter = ('status', 'report__crime_category', 'report__date_time_reported')
    search_fields = ('report__report_id', 'report__location', 'report__crime_category', 'report__sender', 'police__police_id')
    ordering = ('-report__date_time_reported',)
    autocomplete_fields = ['police', 'report']

    def get_report_id(self, obj):
        return obj.report.report_id
    get_report_id.admin_order_field = 'report__report_id'
    get_report_id.short_description = 'Report ID'

    def get_report_location(self, obj):
        return obj.report.location
    get_report_location.admin_order_field = 'report__location'
    get_report_location.short_description = 'Location'

    def get_report_crime_category(self, obj):
        return obj.report.crime_category
    get_report_crime_category.admin_order_field = 'report__crime_category'
    get_report_crime_category.short_description = 'Crime Category'

    def get_report_sender(self, obj):
        return obj.report.sender
    get_report_sender.admin_order_field = 'report__sender'
    get_report_sender.short_description = 'Sender'
