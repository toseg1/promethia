"""
Admin configuration for training sessions models.
"""
from django.contrib import admin
from .models import TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'athlete', 'date', 'time', 'status', 'created_by']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['title', 'athlete__first_name', 'athlete__last_name']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('athlete', 'created_by')