# race_events/admin.py
from django.contrib import admin
from .models import Race, RaceResult


class RaceResultInline(admin.StackedInline):
    model = RaceResult
    extra = 0
    max_num = 1
    fields = ('finish_time', 'overall_position', 'category_position', 'total_participants', 'satisfaction', 'race_report')


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'athlete', 'sport', 'date', 'start_time', 'location', 'goal_type', 'status', 'get_finish_time']
    list_filter = ['sport', 'goal_type', 'status', 'date']
    search_fields = ['title', 'athlete__username', 'athlete__first_name', 'athlete__last_name', 'location']
    ordering = ['date', 'start_time']
    inlines = [RaceResultInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('athlete', 'title', 'sport', 'date', 'start_time')  # CHANGED: name→title, sport_type→sport, time→start_time
        }),
        ('Location', {
            'fields': ('location', 'venue', 'distance')
        }),
        ('Objective', {
            'fields': ('goal_time', 'goal_type', 'status'),  # ADDED: status
            'description': 'What are you aiming for in this race?'
        }),
        ('Notes', {
            'fields': ('description',),  # CHANGED: notes→description
            'classes': ('collapse',)  
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('athlete')
    
    def get_finish_time(self, obj):
        """Display finish time if race has results."""
        if hasattr(obj, 'result') and obj.result.finish_time:
            return obj.result.finish_time
        return "—"
    get_finish_time.short_description = 'Finish Time'

    
  