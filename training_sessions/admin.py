"""
Admin configuration for training sessions models.
"""
from django.contrib import admin
from .models import TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'athlete', 'sport', 'date', 'start_time',
        'duration_minutes', 'distance', 'intensity', 'status' 
    ]

    list_filter = ['sport', 'status', 'intensity', 'date'] 

    search_fields = [
        'title', 'athlete__username', 'athlete__first_name', 
        'athlete__last_name', 'description' 
    ]
   
    ordering = ['date', 'start_time']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('athlete', 'created_by')