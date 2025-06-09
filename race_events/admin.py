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
    list_display = ['name', 'athlete', 'sport_type', 'date', 'location', 'goal_type', 'goal_time', 'get_finish_time']
    list_filter = ['sport_type', 'goal_type', 'date']
    search_fields = ['name', 'athlete__username', 'location']
    ordering = ['date']
    inlines = [RaceResultInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('athlete', 'name', 'sport_type', 'date', 'time')
        }),
        ('Location', {
            'fields': ('location', 'venue', 'distance')
        }),
        ('Objective', {
            'fields': ('goal_time', 'goal_type'),
            'description': 'What are you aiming for in this race?'
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)  # This section can be collapsed
        }),
    )
    
    def get_finish_time(self, obj):
        """Display finish time if race has results."""
        if hasattr(obj, 'result') and obj.result.finish_time:
            return obj.result.finish_time
        return "—"
    get_finish_time.short_description = 'Finish Time'

    
  