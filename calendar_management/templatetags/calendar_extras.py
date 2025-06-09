# calendar_management/templatetags/calendar_extras.py
# Additional template filters for the calendar

from django import template
from datetime import timedelta, datetime
import calendar

register = template.Library()

@register.filter
def duration_format(minutes):
    """Convert minutes to h:m:s format"""
    if not minutes:
        return ""
    
    total_seconds = int(float(minutes) * 60)
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    mins = remaining_seconds // 60
    secs = remaining_seconds % 60
    
    if hours > 0:
        return f"{hours}:{mins:02d}:{secs:02d}"
    else:
        return f"{mins}:{secs:02d}"

@register.filter
def add_days(date, days):
    """Add days to a date"""
    if not date or not days:
        return date
    
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    return date + timedelta(days=int(days))

@register.filter
def month_name(month_num):
    """Get month name from number"""
    try:
        return calendar.month_name[int(month_num)]
    except (ValueError, IndexError):
        return ""

@register.filter
def weekday_short(date):
    """Get short weekday name"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    return date.strftime('%a')

@register.filter
def format_date(date, format_string='Y-m-d'):
    """Format date with custom format"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    return date.strftime(format_string)

@register.filter
def is_today(date):
    """Check if date is today"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    return date == datetime.now().date()

@register.filter
def get_sport_icon(sport):
    """Get FontAwesome icon for sport"""
    icons = {
        'running': 'fa-running',
        'cycling': 'fa-bicycle', 
        'swimming': 'fa-swimmer',
        'trail_running': 'fa-mountain',
        'triathlon': 'fa-medal',
        'duathlon': 'fa-running',
        'race': 'fa-trophy',
        'custom': 'fa-star'
    }
    return icons.get(sport, 'fa-dumbbell')

@register.filter
def get_sport_color(sport):
    """Get color for sport"""
    colors = {
        'running': '#28a745',
        'cycling': '#007bff',
        'swimming': '#17a2b8', 
        'trail_running': '#6f42c1',
        'triathlon': '#fd7e14',
        'duathlon': '#e83e8c',
        'race': '#ffc107',
        'custom': '#6c757d'
    }
    return colors.get(sport, '#6c757d')

@register.inclusion_tag('calendar_management/partials/calendar_day.html')
def render_calendar_day(day_data, month, year, today):
    """Render a calendar day with proper attributes"""
    return {
        'day_data': day_data,
        'month': month,
        'year': year, 
        'today': today,
        'is_today': day_data.get('day') == today.day and month == today.month and year == today.year,
        'date_string': f"{year}-{month:02d}-{day_data.get('day', 1):02d}" if day_data.get('day') else None
    }

@register.inclusion_tag('calendar_management/partials/week_day.html') 
def render_week_day(day_data, today):
    """Render a week day with proper attributes"""
    return {
        'day_data': day_data,
        'today': today,
        'is_today': day_data.get('date') == today,
        'date_string': day_data.get('date').strftime('%Y-%m-%d') if day_data.get('date') else None
    }

# Updated calendar day template
# calendar_management/partials/calendar_day.html
CALENDAR_DAY_TEMPLATE = '''
<div class="calendar-day {% if not day_data.day %}calendar-day-empty{% endif %} {% if is_today %}calendar-day-today{% endif %}"
     {% if date_string %}data-date="{{ date_string }}"{% endif %}
     {% if day_data.day %}tabindex="0"{% endif %}>
    {% if day_data.day %}
        <div class="day-number">{{ day_data.day }}</div>
        <div class="day-events">
            {% for event in day_data.events %}
                {% include 'calendar_management/partials/event_card.html' with event=event %}
            {% endfor %}
        </div>
    {% endif %}
</div>
'''

# Updated week day template  
# calendar_management/partials/week_day.html
WEEK_DAY_TEMPLATE = '''
<div class="week-day {% if is_today %}week-day-today{% endif %}"
     {% if date_string %}data-date="{{ date_string }}"{% endif %}
     tabindex="0">
    <div class="week-day-header">
        <div class="day-name">{{ day_data.day_short|default:day_data.date|weekday_short }}</div>
        <div class="day-number {% if is_today %}today{% endif %}">
            {{ day_data.day_num|default:day_data.date.day }}
        </div>
    </div>
    <div class="week-day-events">
        {% for event in day_data.events %}
            {% include 'calendar_management/partials/event_card.html' with event=event %}
        {% endfor %}
    </div>
</div>
'''

# Calendar view context processor to ensure proper data attributes
# calendar_management/context_processors.py
def calendar_context(request):
    """Add calendar-specific context"""
    from datetime import datetime
    
    today = datetime.now().date()
    current_month = today.month
    current_year = today.year
    
    return {
        'calendar_today': today,
        'calendar_current_month': current_month,
        'calendar_current_year': current_year,
    }

# Usage in main calendar template - update the month view section:
UPDATED_MONTH_VIEW = '''
{% if view_type == 'month' %}
  <!-- Month View -->
  <div class="row">
    <div class="col-12">
      <div class="card card-primary">
        <div class="card-header" data-current-month="{{ month }}" data-current-year="{{ year }}">
          <div class="row align-items-center">
            <div class="col-md-6">
              <h3 class="card-title mb-0">
                <i class="fas fa-calendar mr-2"></i>
                {{ month|month_name }} {{ year }}
              </h3>
            </div>
            <div class="col-md-6">
              <div class="float-right">
                <!-- Month Navigation -->
                <div class="btn-group" role="group">
                  {% if month == 1 %}
                    <a href="{% url 'calendar_management:view' %}?view=month&year={{ year|add:'-1' }}&month=12" 
                       class="btn btn-link btn-sm text-white">
                      <i class="fas fa-chevron-left"></i>
                    </a>
                  {% else %}
                    <a href="{% url 'calendar_management:view' %}?view=month&year={{ year }}&month={{ month|add:'-1' }}" 
                       class="btn btn-link btn-sm text-white">
                      <i class="fas fa-chevron-left"></i>
                    </a>
                  {% endif %}
                  
                  <a href="{% url 'calendar_management:view' %}?view=month" 
                     class="btn btn-link btn-sm text-white">
                    Today
                  </a>
                  
                  {% if month == 12 %}
                    <a href="{% url 'calendar_management:view' %}?view=month&year={{ year|add:'1' }}&month=1" 
                       class="btn btn-link btn-sm text-white">
                      <i class="fas fa-chevron-right"></i>
                    </a>
                  {% else %}
                    <a href="{% url 'calendar_management:view' %}?view=month&year={{ year }}&month={{ month|add:'1' }}" 
                       class="btn btn-link btn-sm text-white">
                      <i class="fas fa-chevron-right"></i>
                    </a>
                  {% endif %}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="card-body p-0">
          <div class="calendar-month">
            <!-- Calendar Header -->
            <div class="calendar-header">
              <div class="calendar-day-header">Mon</div>
              <div class="calendar-day-header">Tue</div>
              <div class="calendar-day-header">Wed</div>
              <div class="calendar-day-header">Thu</div>
              <div class="calendar-day-header">Fri</div>
              <div class="calendar-day-header">Sat</div>
              <div class="calendar-day-header">Sun</div>
            </div>
            
            <!-- Calendar Body -->
            <div class="calendar-body">
              {% if calendar_data %}
                {% for week in calendar_data %}
                  <div class="calendar-week">
                    {% for day_data in week %}
                      {% render_calendar_day day_data month year today %}
                    {% endfor %}
                  </div>
                {% endfor %}
              {% endif %}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{% endif %}
'''