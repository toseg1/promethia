"""
Admin configuration for user management models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, CoachAthleteRelationship


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


@admin.register(CoachAthleteRelationship)
class CoachAthleteRelationshipAdmin(admin.ModelAdmin):
    list_display = ['coach', 'athlete', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['coach__first_name', 'coach__last_name', 'athlete__first_name', 'athlete__last_name']


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)