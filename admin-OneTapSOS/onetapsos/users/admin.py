from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Define an inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    # Optional: To display phone_number in the user list
    def phone_number(self, instance):
        return instance.profile.phone_number if hasattr(instance, 'profile') else ''
    phone_number.short_description = 'Phone Number'

    list_display = BaseUserAdmin.list_display + ('phone_number',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
