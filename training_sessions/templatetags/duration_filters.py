# Create this file: training_sessions/templatetags/__init__.py
# (empty file, just create it)

# Create this file: training_sessions/templatetags/duration_filters.py
from django import template

register = template.Library()

@register.filter
def duration_hms(minutes):
    """Convert minutes to h:m:s format"""
    if not minutes:
        return "0:00:00"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    seconds = 0  # Since we only store minutes, seconds will always be 0
    
    return f"{hours}:{remaining_minutes:02d}:{seconds:02d}"