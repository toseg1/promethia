# calendar_management/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta, date, time as datetime_time
import calendar
from collections import defaultdict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from .models import CustomEvent
from race_events.models import Race
from django.contrib.auth.models import User
from django.views.generic import TemplateView
import calendar as cal
from user_management.views import get_current_view_mode
from training_calendar.utils.logging_helpers import get_logger, log_error, log_warning, log_info
from training_calendar.utils.messages import UserMessages

logger = get_logger('calendar_management')

@login_required
def calendar_view(request):
    """Enhanced calendar view with proper event data"""

    view_type = request.GET.get('view', 'month')
    today = date.today()
    
    if view_type == 'week':
        return render_week_view(request, today)
    else:
        return render_month_view(request, today)

def render_month_view(request, today):
    """Render month calendar view"""
    # Handle empty parameters safely
    year_param = request.GET.get('year', '')
    month_param = request.GET.get('month', '')
    
    year = int(year_param) if year_param else today.year
    month = int(month_param) if month_param else today.month
    
    # Get calendar data
    cal = calendar.Calendar(firstweekday=0)  # Monday = 0
    month_days = cal.monthdayscalendar(year, month)
    
    # Get all events for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    events = get_month_events(request.user, start_date, end_date)
    
    volume_data = get_training_volume_by_sport(request.user, start_date, end_date)

    # Organize events by date
    events_by_date = defaultdict(list)
    for event in events:
        event_date = event.get('date')
        if event_date:
            events_by_date[event_date.day].append(event)
    
    # Build calendar data structure
    calendar_data = []
    for week in month_days:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': None, 'events': []})
            else:
                day_events = events_by_date.get(day, [])
                week_data.append({
                    'day': day, 
                    'events': day_events,
                    'date': date(year, month, day)
                })
        calendar_data.append(week_data)
    
    context = {
        'calendar_data': calendar_data,
        'month': month,
        'year': year,
        'today': today,
        'view_type': 'month',
        'events': events,
        'volume_data': volume_data,
    }
    
    return render(request, 'calendar_management/calendar_athlete.html', context)

def render_week_view(request, today):
    """Render week calendar view"""
    week_start_str = request.GET.get('week_start')
    
    if week_start_str:
        week_start_date = datetime.strptime(week_start_str, '%Y-%m-%d').date()
    else:
        days_since_monday = today.weekday()
        week_start_date = today - timedelta(days=days_since_monday)
    
    week_days = []
    for i in range(7):
        current_date = week_start_date + timedelta(days=i)
        week_days.append({
            'date': current_date,
            'day_short': current_date.strftime('%a'),
            'day_num': current_date.day,
            'events': []
        })
    
    week_end_date = week_start_date + timedelta(days=6)
    week_events = get_month_events(request.user, week_start_date, week_end_date)

    # Get training volume data for the week
    volume_data = get_training_volume_by_sport(request.user, week_start_date, week_end_date)

    
    for event in week_events:
        event_date = event.get('date')
        if event_date:
            for day_data in week_days:
                if day_data['date'] == event_date:
                    day_data['events'].append(event)
                    break
    
    context = {
        'week_days': week_days,
        'week_events': week_events,
        'week_start_date': week_start_date,
        'today': today,
        'view_type': 'week',
        'hours': range(6, 24),
        'volume_data': volume_data,
    }
    
    return render(request, 'calendar_management/calendar_athlete.html', context)

def get_month_events(user, start_date, end_date):
    """Get all events with proper error handling and logging."""
    events = []
    
    try:
        # Get athlete users
        athlete_users = [user]
        if hasattr(user, 'profile') and user.profile.is_coach:
            try:
                from user_management.models import CoachAthleteRelationship
                coach_athletes = CoachAthleteRelationship.objects.filter(
                    coach=user, status='accepted'
                ).select_related('athlete')
                athlete_users.extend([rel.athlete for rel in coach_athletes])
            except Exception as e:
                log_error(logger, "Error loading coach-athlete relationships", e, user=user.username)
        
        # TRAINING SESSIONS - FIXED with proper logging
        try:
            from training_sessions.models import TrainingSession
            sessions = TrainingSession.objects.filter(
                athlete__in=athlete_users,
                date__range=[start_date, end_date]
            ).select_related('athlete')
            
            for session in sessions:
                try:
                    events.append({
                        'id': session.id,
                        'title': session.title,
                        'date': session.date,
                        'start_time': session.start_time,
                        'duration': session.duration_minutes,
                        'distance': session.distance,
                        'sport': session.sport,
                        'event_type': 'training_session',
                        'status': session.status,
                        'athlete': session.athlete,
                        'description': session.description,
                        'intensity': session.intensity,
                        'duration_days': 1,
                        'color': session.sport_color,
                        'icon': session.sport_icon,
                    })
                except AttributeError as e:
                    log_error(logger, f"Error processing training session {session.id}", e, 
                             session_id=session.id, user=user.username)
                    continue
                    
        except ImportError:
            log_warning(logger, "TrainingSession model not available", user=user.username)
        except Exception as e:
            log_error(logger, "Error loading training sessions", e, 
                     user=user.username, date_range=f"{start_date} to {end_date}")
        
        # RACE EVENTS - FIXED with proper logging
        try:
            from race_events.models import Race
            races = Race.objects.filter(
                athlete__in=athlete_users,
                date__range=[start_date, end_date]
            ).select_related('athlete')
            
            for race in races:
                try:
                    events.append({
                        'id': race.id,
                        'title': race.title,
                        'date': race.date,
                        'start_time': race.start_time,
                        'distance': race.distance,
                        'sport': race.sport,
                        'event_type': 'race',
                        'status': race.status,
                        'athlete': race.athlete,
                        'description': race.description,
                        'location': race.location,
                        'venue': race.venue,
                        'goal_time': race.goal_time,
                        'goal_type': race.goal_type,
                        'duration_days': 1,
                    })
                except AttributeError as e:
                    log_error(logger, f"Error processing race {race.id}", e,
                             race_id=race.id, user=user.username)
                    continue
                    
        except ImportError:
            log_warning(logger, "Race model not available", user=user.username)
        except Exception as e:
            log_error(logger, "Error loading race events", e,
                     user=user.username, date_range=f"{start_date} to {end_date}")
        
        # CUSTOM EVENTS - Already clean, just add logging
        try:
            from calendar_management.models import CustomEvent
            custom_events = CustomEvent.objects.filter(
                user__in=athlete_users,
                start_date__range=[start_date, end_date]
            )
            
            for custom_event in custom_events:
                events.append({
                    'id': custom_event.id,
                    'title': custom_event.title,
                    'date': custom_event.start_date,
                    'event_type': 'custom',
                    'sport': 'custom',
                    'athlete': custom_event.user,
                    'description': custom_event.description or '',
                    'color': custom_event.color or '#6c757d',
                    'duration_days': (custom_event.end_date - custom_event.start_date).days + 1,
                    'start_time': datetime_time(0, 0),
                })
                
        except ImportError:
            log_warning(logger, "CustomEvent model not available", user=user.username)
        except Exception as e:
            log_error(logger, "Error loading custom events", e,
                     user=user.username, date_range=f"{start_date} to {end_date}")
            
    except Exception as e:
        log_error(logger, "Critical error in get_month_events", e,
                 user=user.username, date_range=f"{start_date} to {end_date}")
    
    # Sort events by date and time
    events.sort(key=lambda x: (
        x.get('date', start_date),
        x.get('start_time') or datetime_time(0, 0)
    ))
    
    log_info(logger, f"Loaded {len(events)} events for calendar", 
             user=user.username, event_count=len(events))
    
    return events

@login_required
def create_custom_event(request, event_id=None):
    """Create a new custom event or edit an existing one"""
    try:
        from .forms import CustomEventForm
        from .models import CustomEvent
        from datetime import timedelta
        from django.shortcuts import get_object_or_404
    except ImportError as e:
        from django.http import HttpResponse
        return HttpResponse(f"Form import error: {e}")
    
    # Check if we're editing an existing event
    event = None
    if event_id:
        event = get_object_or_404(CustomEvent, id=event_id, user=request.user)
        
    if request.method == 'POST':
        print("Form submitted!") # Debug print
        form = CustomEventForm(request.POST, instance=event)
        print(f"Form data: {request.POST}") # Debug print
        
        if form.is_valid():
            print("Form is valid!") # Debug print
            
            # Get the form data
            title = form.cleaned_data['title']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            description = form.cleaned_data.get('description', '')
            color = form.cleaned_data.get('color', '#6c757d')
            
            if event_id:
                # Editing existing event - update it
                event.title = title
                event.start_date = start_date
                event.end_date = end_date
                event.description = description
                event.color = color
                event.save()
                
                from django.contrib import messages
                messages.success(request, f'Custom event "{title}" updated successfully!')
            else:
                # Creating new event - create individual events for each day
                current_date = start_date
                created_events = []
                
                while current_date <= end_date:
                    custom_event = CustomEvent(
                        user=request.user,
                        title=title,
                        start_date=current_date,
                        end_date=current_date,  # Each entry is single-day
                        description=description,
                        color=color
                    )
                    custom_event.save()
                    created_events.append(custom_event)
                    current_date += timedelta(days=1)
                
                from django.contrib import messages
                if len(created_events) == 1:
                    messages.success(request, f'Custom event "{title}" created successfully!')
                else:
                    messages.success(request, f'Multi-day event "{title}" created for {len(created_events)} days!')
            
            return redirect('calendar_management:view')
        else:
            print(f"Form errors: {form.errors}") # Debug print
    else:
        if event_id:
            # Pre-populate form for editing
            form = CustomEventForm(instance=event)
        else:
            # Pre-fill with date if provided in URL for new event
            initial_date = request.GET.get('date')
            initial_data = {}
            if initial_date:
                initial_data['start_date'] = initial_date
                initial_data['end_date'] = initial_date
            form = CustomEventForm(initial=initial_data)
    
    context = {
        'form': form,
        'event': event,
        'is_editing': bool(event_id),
    }
    
    return render(request, 'calendar_management/create_custom_event.html', context)


def delete_custom_event(request, event_id):
    """Delete a custom event"""
    try:
        from .models import CustomEvent
        from django.shortcuts import get_object_or_404
    except ImportError as e:
        from django.http import HttpResponse
        return HttpResponse(f"Model import error: {e}")
    
    event = get_object_or_404(CustomEvent, id=event_id, user=request.user)
    event_title = event.title
    
    # Delete the event
    event.delete()
    
    from django.contrib import messages
    messages.success(request, f'Custom event "{event_title}" has been permanently deleted from your calendar.')
    
    return redirect('calendar_management:view')

@login_required
def custom_event_detail(request, event_id):
    """Display custom event details"""
    from calendar_management.models import CustomEvent
    
    event = get_object_or_404(CustomEvent, id=event_id, user=request.user)
    
    # Calculate duration in days
    duration_days = (event.end_date - event.start_date).days + 1
    
    context = {
        'event': event,
        'duration_days': duration_days,
    }
    
    return render(request, 'calendar_management/custom_event_detail.html', context)

# Updated coach views with proper athlete filtering

class CoachCalendarView(LoginRequiredMixin, TemplateView):
    """Coach calendar view showing only races of assigned athletes."""
    
    template_name = 'calendar_management/calendar_coach.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check current view mode instead of user role
        current_view = get_current_view_mode(request)
        
        if current_view != 'coach':
            return redirect('calendar_management:view')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_coach_athletes(self):
        """Get athletes assigned to this coach."""
        try:
            from user_management.models import CoachAthleteRelationship
            
            # DEBUG: Print all unique status values
            all_statuses = CoachAthleteRelationship.objects.values_list('status', flat=True).distinct()
            print(f"Available status values: {list(all_statuses)}")
            
            # DEBUG: Print relationships for this coach
            coach_relationships = CoachAthleteRelationship.objects.filter(coach=self.request.user)
            for rel in coach_relationships:
                print(f"Athlete: {rel.athlete}, Status: {rel.status}")
            
            # Get active relationships - adjust the status value based on your data
            relationships = CoachAthleteRelationship.objects.filter(
                coach=self.request.user,
                status='active'  # Change this based on your actual status values
            ).select_related('athlete')
            
            return User.objects.filter(
                id__in=relationships.values_list('athlete_id', flat=True),
                is_active=True
            )
        except ImportError as e:
            print(f"Import error: {e}")
            return User.objects.none()

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current view mode
        current_view = get_current_view_mode(self.request)
        
        # Get only athletes with coach relationship
        coach_athletes = self.get_coach_athletes()
        
        # Get view parameters
        view_type = self.request.GET.get('view', 'month')
        year = int(self.request.GET.get('year', datetime.now().year))
        month = int(self.request.GET.get('month', datetime.now().month))
        week_start = self.request.GET.get('week_start')
        
        context.update({
            'current_view': current_view,
            'coach_athletes': coach_athletes,
            'view_type': view_type,
            'year': year,
            'month': month,
            'today': datetime.now().date(),
        })
        
        if view_type == 'month':
            context.update(self._get_month_context(year, month, coach_athletes))
        else:  # week view
            if week_start:
                week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
            else:
                today = datetime.now().date()
                week_start_date = today - timedelta(days=today.weekday())
            
            context.update(self._get_week_context(week_start_date, coach_athletes))
        
        return context
    
    def _get_month_context(self, year, month, coach_athletes):
        """Get calendar data for month view."""
        try:
            from race_events.models import Race
            
            # Get races for coached athletes only
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            races = Race.objects.filter(
                athlete__in=coach_athletes,
                date__range=[start_date, end_date]
            ).select_related('athlete').order_by('date', 'start_time')
            
            # Build calendar structure
            calendar_data = []
            cal_month = cal.monthcalendar(year, month)
            
            for week in cal_month:
                week_data = []
                for day in week:
                    if day == 0:
                        week_data.append({'day': None, 'events': []})
                    else:
                        day_date = datetime(year, month, day).date()
                        day_races = [race for race in races if race.date == day_date]
                        week_data.append({
                            'day': day,
                            'events': day_races
                        })
                calendar_data.append(week_data)
            
            # Add statistics for coached athletes only
            upcoming_races = races.filter(date__gte=datetime.now().date()).count()
            recent_races = Race.objects.filter(
                athlete__in=coach_athletes,
                date__gte=datetime.now().date() - timedelta(days=30),
                date__lt=datetime.now().date()
            ).count()
            
            # Count athletes who have races
            athletes_with_races = races.values('athlete').distinct().count()
            
            return {
                'calendar_data': calendar_data,
                'upcoming_races_count': upcoming_races,
                'recent_races_count': recent_races,
                'active_athletes_count': athletes_with_races,
            }
            
        except ImportError:
            return {
                'calendar_data': [],
                'upcoming_races_count': 0,
                'recent_races_count': 0,
                'active_athletes_count': 0,
            }
    
    def _get_week_context(self, week_start_date, coach_athletes):
        """Get calendar data for week view."""
        try:
            from race_events.models import Race
            
            week_end_date = week_start_date + timedelta(days=6)
            
            races = Race.objects.filter(
                athlete__in=coach_athletes,
                date__range=[week_start_date, week_end_date]
            ).select_related('athlete').order_by('date', 'start_time')
            
        except ImportError:
            races = []
        
        # Build week days
        week_days = []
        for i in range(7):
            day_date = week_start_date + timedelta(days=i)
            week_days.append({
                'date': day_date,
                'day_num': day_date.day,
                'day_short': day_date.strftime('%a'),
            })
        
        return {
            'week_start_date': week_start_date,
            'week_days': week_days,
            'week_events': races,
        }


class CoachAthleteCalendarView(LoginRequiredMixin, TemplateView):
    """Coach viewing a specific athlete's full calendar."""
    
    template_name = 'calendar_management/calendar_athlete.html'
    
    def dispatch(self, request, *args, **kwargs):
        current_view = get_current_view_mode(request)
        
        if current_view != 'coach':
            return redirect('calendar_management:view')
        
        # Verify coach has relationship with this athlete
        athlete_id = kwargs.get('athlete_id')
        if not self.can_view_athlete(athlete_id):
            from django.contrib import messages
            messages.error(request, "You don't have permission to view this athlete's calendar.")
            return redirect('calendar_management:coach_view')
            
        return super().dispatch(request, *args, **kwargs)
    
    def can_view_athlete(self, athlete_id):
        """Check if coach has permission to view this athlete."""
        try:
            from user_management.models import CoachAthleteRelationship
            
            return CoachAthleteRelationship.objects.filter(
                coach=self.request.user,
                athlete_id=athlete_id,
            ).exists()
        except ImportError:
            # Fallback: check other possible relationship structures
            try:
                athlete = User.objects.get(id=athlete_id)
                return hasattr(athlete, 'coach') and athlete.coach == self.request.user
            except:
                return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        athlete_id = kwargs.get('athlete_id')
        athlete = get_object_or_404(User, id=athlete_id, is_active=True)
        
        current_view = get_current_view_mode(self.request)
        
        view_type = self.request.GET.get('view', 'month')
        year = int(self.request.GET.get('year', datetime.now().year))
        month = int(self.request.GET.get('month', datetime.now().month))
        week_start = self.request.GET.get('week_start')
        
        context.update({
            'current_view': current_view,
            'viewing_athlete': athlete,
            'is_coach_view': True,
            'view_type': view_type,
            'year': year,
            'month': month,
            'today': datetime.now().date(),
        })
        
        if view_type == 'month':
            context.update(self._get_athlete_month_context(year, month, athlete))
        else:  # week view
            if week_start:
                week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
            else:
                today = datetime.now().date()
                week_start_date = today - timedelta(days=today.weekday())
            
            context.update(self._get_athlete_week_context(week_start_date, athlete))
        
        # Add athlete statistics
        try:
            from race_events.models import Race
            
            context['athlete_upcoming_races'] = Race.objects.filter(
                athlete=athlete,
                date__gte=datetime.now().date()
            ).count()
            
            # Events this month
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            month_events = get_month_events(athlete, start_date, end_date)
            context['athlete_events_this_month'] = len(month_events)
            
        except:
            context['athlete_upcoming_races'] = 0
            context['athlete_events_this_month'] = 0
        
        return context
    
    def _get_athlete_month_context(self, year, month, athlete):
        """Get all events for the athlete in the month with standardized format."""
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # Use the existing get_month_events function to get standardized event data
        events = get_month_events(athlete, start_date, end_date)

        volume_data = get_training_volume_by_sport(athlete, start_date, end_date)
        
        # Organize events by date
        events_by_date = defaultdict(list)
        for event in events:
            event_date = event.get('date')
            if event_date:
                events_by_date[event_date.day].append(event)
        
        # Build calendar structure
        calendar_data = []
        cal_month = cal.monthcalendar(year, month)
        
        for week in cal_month:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({'day': None, 'events': []})
                else:
                    day_date = datetime(year, month, day).date()
                    day_events = events_by_date.get(day, [])
                    week_data.append({
                        'day': day,
                        'events': day_events,
                        'date': day_date
                    })
            calendar_data.append(week_data)
        
        return {
            'calendar_data': calendar_data,
            'volume_data': volume_data,
        }
    
    def _get_athlete_week_context(self, week_start_date, athlete):
        """Get all events for the athlete in the week with standardized format."""
        week_end_date = week_start_date + timedelta(days=6)
        
        # Use the existing get_month_events function to get standardized event data
        week_events = get_month_events(athlete, week_start_date, week_end_date)

        volume_data = get_training_volume_by_sport(athlete, week_start_date, week_end_date)
        
        # Build week days
        week_days = []
        for i in range(7):
            day_date = week_start_date + timedelta(days=i)
            week_days.append({
                'date': day_date,
                'day_num': day_date.day,
                'day_short': day_date.strftime('%a'),
            })
        
        return {
            'week_start_date': week_start_date,
            'week_days': week_days,
            'week_events': week_events,
            'volume_data': volume_data,
        }
    
def get_training_volume_by_sport(user, start_date, end_date):
    """Calculate training volume by sport for a date range - ONLY COMPLETED sessions"""
    from training_sessions.models import TrainingSession
    from collections import defaultdict
    
    # Get athlete users (including coached athletes if user is coach)
    athlete_users = [user]
    if hasattr(user, 'profile') and user.profile.role == 'coach':
        from user_management.models import CoachAthleteRelationship
        coach_athletes = CoachAthleteRelationship.objects.filter(
            coach=user, status='accepted'
        ).select_related('athlete')
        athlete_users.extend([rel.athlete for rel in coach_athletes])
    
    # Get ONLY COMPLETED training sessions in date range
    sessions = TrainingSession.objects.filter(
        athlete__in=athlete_users,
        date__range=[start_date, end_date],
        status='completed'  # FIXED: Only count completed sessions
    ).select_related('athlete')
    
    # Initialize volume counters
    volume_data = {
        'total': {'sessions': 0, 'duration': 0},
        'running': {'sessions': 0, 'duration': 0},
        'cycling': {'sessions': 0, 'duration': 0}, 
        'swimming': {'sessions': 0, 'duration': 0},
    }
    
    # Calculate volumes
    for session in sessions:
        duration = session.duration_minutes or 0
        sport = session.sport or 'other'
        
        # Add to total
        volume_data['total']['sessions'] += 1
        volume_data['total']['duration'] += duration
        
        # Add to sport-specific (running includes trail)
        if sport in ['running', 'trail']:
            volume_data['running']['sessions'] += 1
            volume_data['running']['duration'] += duration
        elif sport == 'cycling':
            volume_data['cycling']['sessions'] += 1
            volume_data['cycling']['duration'] += duration
        elif sport == 'swimming':
            volume_data['swimming']['sessions'] += 1
            volume_data['swimming']['duration'] += duration
    
    # Format durations as hours:minutes
    for sport_data in volume_data.values():
        hours = sport_data['duration'] // 60
        minutes = sport_data['duration'] % 60
        sport_data['duration_formatted'] = f"{hours}h {minutes:02d}m"
        
        # Add hours as decimal for charts
        sport_data['duration_hours'] = round(sport_data['duration'] / 60, 1)
    
    return volume_data