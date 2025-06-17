"""
Calendar and training session views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta
import calendar
from .models import TrainingSession
from .forms import TrainingSessionForm, TrainingRepetitionFormSet
from user_management.models import CoachAthleteRelationship
from datetime import datetime, timedelta, date, time as datetime_time
from collections import defaultdict
from django.contrib.auth.models import User
from user_management.views import get_current_view_mode


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
        'events': events
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
        'hours': range(6, 24)
    }
    
    return render(request, 'calendar_management/calendar_athlete.html', context)

def get_month_events(user, start_date, end_date):
    """Get real events from your models"""
    events = []
    
    try:
        # Training Sessions
        try:
            from training_sessions.models import TrainingSession
            sessions = TrainingSession.objects.filter(
                athlete=user,
                date__range=[start_date, end_date]
            ).select_related('athlete')
            
            for session in sessions:
                events.append({
                    'id': session.id,
                    'title': getattr(session, 'session_type', None) or getattr(session, 'title', None) or 'Training Session',
                    'date': session.date,
                    'start_time': getattr(session, 'start_time', None) or datetime_time(1, 0),  # Default to 0:00 AM
                    'duration': getattr(session, 'duration_minutes', None) or getattr(session, 'duration', None),
                    'distance': getattr(session, 'distance', None),
                    'sport': getattr(session, 'sport', 'running'),
                    'event_type': 'training_session',
                    'status': getattr(session, 'status', 'scheduled'),
                    'athlete': session.athlete,
                    'description': getattr(session, 'notes', '') or getattr(session, 'description', ''),
                    'intensity': getattr(session, 'intensity', None),
                    'duration_days': 1,
                })
        except ImportError:
            print("TrainingSession model not found")
        except Exception as e:
            print(f"Training sessions error: {e}")
        
        # Race Events  
        try:
            from race_events.models import Race
            races = Race.objects.filter(
                athlete=user,
                date__range=[start_date, end_date]
            ).select_related('athlete')
            
            for race in races:
                events.append({
                    'id': race.id,
                    'title': getattr(race, 'name', None) or getattr(race, 'title', None) or 'Race Event',
                    'date': race.date,
                    'start_time': getattr(race, 'start_time', None) or datetime_time(1, 0),  # Default to 0:00 AM for races
                    'distance': getattr(race, 'distance', None),
                    'sport': getattr(race, 'race_type', 'race'),
                    'event_type': 'race',
                    'status': getattr(race, 'status', 'scheduled'),
                    'athlete': race.athlete,
                    'description': getattr(race, 'description', ''),
                    'location': getattr(race, 'location', ''),
                    'race_type': getattr(race, 'race_type', ''),
                    'duration_days': 1,
                })
        except ImportError:
            print("Race model not found")
        except Exception as e:
            print(f"Race events error: {e}")
        
        # Custom Events
        try:
            from calendar_management.models import CustomEvent
            
            custom_events = CustomEvent.objects.filter(
                user=user,
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
                    'description': custom_event.note or '',
                    'color': custom_event.color or '#6c757d',
                    'duration_days': 1,  # Each entry is single-day now
                    'start_time': datetime_time(0, 0),
                })
        except ImportError:
            print("CustomEvent model not found")
        except Exception as e:
            print(f"Custom events error: {e}")
        
    except Exception as e:
        print(f"Overall get_month_events error: {e}")
        import traceback
        traceback.print_exc()
    
    # Sort events by date only (since custom events don't have start_time)
    events.sort(key=lambda x: x.get('date', start_date))
    
    return events


@login_required
def session_create(request):
    """Create new training session with optional repetitions."""
    # Get parameters from URL
    date_param = request.GET.get('date')
    athlete_id = request.GET.get('athlete_id')
    current_view = request.GET.get('view', 'athlete')
    
    selected_athlete = None
    
    initial_data = {}
    
    # Handle date pre-filling
    if date_param:
        try:
            from datetime import datetime
            session_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            initial_data['date'] = session_date
        except ValueError:
            pass
    
    # Handle athlete selection
    if athlete_id:
        try:
            selected_athlete = get_object_or_404(User, id=athlete_id)
            # Verify permission if coach
            if request.user.profile.role == 'coach':
                CoachAthleteRelationship.objects.get(
                    coach=request.user,
                    athlete=selected_athlete,
                    status='active'
                )
            initial_data['athlete'] = selected_athlete
        except (User.DoesNotExist, CoachAthleteRelationship.DoesNotExist):
            pass
    
    # Prepare athlete choices for coaches
    athlete_choices = None
    if request.user.profile.role == 'coach':
        if current_view == 'coach':
            coached_relationships = CoachAthleteRelationship.objects.filter(
                coach=request.user,
                status='active'
            )
            athlete_choices = [(rel.athlete.id, rel.athlete.get_full_name()) 
                             for rel in coached_relationships]
    
    if request.method == 'POST':
        form = TrainingSessionForm(
            request.POST, 
            athlete_choices=athlete_choices,
            user=request.user,
            current_view=current_view
        )
        
        repetition_formset = TrainingRepetitionFormSet(request.POST, prefix='repetitions')

        # SIMPLE DEBUG: Just check the POST data
        print("🔍 DEBUG: Raw POST data:")
        for key, value in request.POST.items():
            if 'repetitions' in key:
                print(f"  {key} = {value}")

        print(f"🔍 DEBUG: Formset is bound: {repetition_formset.is_bound}")
        print(f"🔍 DEBUG: Formset prefix: {repetition_formset.prefix}")

        
        if form.is_valid() and repetition_formset.is_valid():
            session = form.save(commit=False)
            session.created_by = request.user
            
            # Auto-assign athlete for athlete users if not specified
            if request.user.profile.role == 'athlete' and not session.athlete:
                session.athlete = request.user
            
            session.save()
            
            # Save repetitions
            repetitions = repetition_formset.save(commit=False)
            for repetition in repetitions:
                repetition.session = session
                repetition.save()
            
            # Handle deleted repetitions
            for obj in repetition_formset.deleted_objects:
                obj.delete()
            
            messages.success(request, 'Training session created successfully!')
            return redirect('session_detail', session.id)
    else:
        form = TrainingSessionForm(
            initial=initial_data,
            athlete_choices=athlete_choices,
            user=request.user,
            current_view=current_view
        )
        repetition_formset = TrainingRepetitionFormSet(prefix='repetitions')
    
    context = {
        'form': form,
        'repetition_formset': repetition_formset,
        'selected_athlete': selected_athlete,
        'current_view': current_view,
        'page_title': 'Create Training Session'
    }
    
    return render(request, 'training_sessions/session_form.html', context)


@login_required
def session_detail(request, session_id):
    """View training session details."""
    session = get_object_or_404(
        TrainingSession.objects.prefetch_related('repetitions'), 
        id=session_id
    )
    
    # Check if user can edit this session
    can_edit = (
        session.athlete == request.user or
        session.created_by == request.user or
        (hasattr(request.user, 'profile') and 
         request.user.profile.role == 'coach' and 
         CoachAthleteRelationship.objects.filter(
             coach=request.user, 
             athlete=session.athlete, 
             status='active'
         ).exists())
    )
    
    context = {
        'session': session,
        'can_edit': can_edit
    }
    
    return render(request, 'training_sessions/session_detail.html', context)


@login_required
def session_edit(request, session_id):
    """Edit training session with optional repetitions."""
    session = get_object_or_404(TrainingSession, id=session_id)
    
    # Check permissions
    can_edit = (
        session.athlete == request.user or
        session.created_by == request.user or
        (request.user.profile.is_coach and 
         CoachAthleteRelationship.objects.filter(
             coach=request.user, 
             athlete=session.athlete, 
             status='active'
         ).exists())
    )
    
    if not can_edit:
        messages.error(request, 'You do not have permission to edit this session.')
        return redirect('dashboard')
    
    # Prepare athlete choices
    athlete_choices = None
    if request.user.profile.role == 'coach':
        coached_relationships = CoachAthleteRelationship.objects.filter(
            coach=request.user,
            status='active'
        )
        athlete_choices = [(rel.athlete.id, rel.athlete.get_full_name()) 
                          for rel in coached_relationships]
    
    if request.method == 'POST':
        form = TrainingSessionForm(
            request.POST, 
            instance=session, 
            athlete_choices=athlete_choices
        )
        
        repetition_formset = TrainingRepetitionFormSet(
            request.POST, 
            instance=session
        )
        
        if form.is_valid() and repetition_formset.is_valid():
            session = form.save()
            
            # Save repetitions
            repetitions = repetition_formset.save(commit=False)
            for repetition in repetitions:
                repetition.session = session
                repetition.save()
            
            # Handle deleted repetitions
            for obj in repetition_formset.deleted_objects:
                obj.delete()
            
            messages.success(request, 'Training session updated successfully!')
            return redirect('session_detail', session_id=session.id)
    else:
        form = TrainingSessionForm(instance=session, athlete_choices=athlete_choices)
        repetition_formset = TrainingRepetitionFormSet(instance=session)
    
    return render(request, 'training_sessions/session_form.html', {
        'form': form, 
        'repetition_formset': repetition_formset,
        'title': 'Edit Training Session',
        'session': session
    })


@login_required
def session_delete(request, session_id):
    """Delete training session."""
    session = get_object_or_404(TrainingSession, id=session_id)
    
    # Check permissions (same as edit)
    can_delete = (
        session.athlete == request.user or
        session.created_by == request.user or
        (request.user.profile.is_coach and 
         CoachAthleteRelationship.objects.filter(
             coach=request.user, 
             athlete=session.athlete, 
             status='active'
         ).exists())
    )
    
    if not can_delete:
        messages.error(request, 'You do not have permission to delete this session.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Training session deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'training_sessions/session_confirm_delete.html', {'session': session})

@login_required
def session_completed(request, session_id):
    """Mark training session as completed."""
    session = get_object_or_404(TrainingSession, id=session_id)
    
    # Check permissions (same as edit)
    can_complete = (
        session.athlete == request.user or
        session.created_by == request.user or
        (request.user.profile.is_coach and
         CoachAthleteRelationship.objects.filter(
             coach=request.user,
             athlete=session.athlete,
             status='active'
         ).exists())
    )
    
    if not can_complete:
        messages.error(request, 'You do not have permission to complete this session.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        session.status = 'completed'
        session.save()
        messages.success(request, 'Training session marked as completed!')
        return redirect('session_detail', session_id=session.id)
    
    return render(request, 'training_sessions/session_confirm_complete.html', {'session': session})