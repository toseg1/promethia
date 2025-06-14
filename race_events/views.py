"""
Views for race_events app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from .models import Race, RaceResult
from .forms import RaceForm
from user_management.views import get_current_view_mode
from training_calendar.utils.logging_helpers import get_logger, log_error, log_info, log_user_action, log_warning
from training_calendar.utils.messages import UserMessages

logger = get_logger('race_events')


@login_required
def race_list(request):
    """
    List races based on current view mode:
    - Athletes see only their races
    - Coaches see all athletes' races with filtering options
    """
    current_view = get_current_view_mode(request)
    
    if current_view == 'coach':  # Adjust this condition based on your view mode values
        return coach_race_list_view(request)
    else:
        return athlete_race_list_view(request)


def athlete_race_list_view(request):
    """List user's races (original functionality)."""
    races = Race.objects.filter(athlete=request.user).order_by('date')
    return render(request, 'race_events/race_list.html', {'races': races})


def coach_race_list_view(request):
    """Display races only for athletes that this coach is responsible for"""
    
    from django.contrib.auth.models import User
    from user_management.models import CoachAthleteRelationship
    
    coached_athlete_ids = CoachAthleteRelationship.objects.filter(
        coach=request.user,
        status='active'  # Only show races for active coaching relationships
    ).values_list('athlete_id', flat=True)
    
    if not coached_athlete_ids:
        # Coach has no active athletes assigned
        races_queryset = Race.objects.none()
        messages.info(request, 
            "You don't have any active athletes assigned. Add new athlete to set up coaching relationships.")
    else:
        races_queryset = Race.objects.filter(athlete_id__in=coached_athlete_ids)
    
    # Apply filters
    athlete_filter = request.GET.get('athlete')
    sport_filter = request.GET.get('sport')
    status_filter = request.GET.get('status')
    
    if athlete_filter:
        races_queryset = races_queryset.filter(athlete_id=athlete_filter)
    
    if sport_filter:
        races_queryset = races_queryset.filter(sport_type=sport_filter)
    
    # Status filtering
    today = timezone.now().date()
    if status_filter == 'upcoming':
        races_queryset = races_queryset.filter(date__gte=today)
    elif status_filter == 'completed':
        races_queryset = races_queryset.filter(
            date__lt=today,
            result__isnull=False
        )
    elif status_filter == 'past_no_results':
        races_queryset = races_queryset.filter(
            date__lt=today,
            result__isnull=True
        )
    
    # Order by date (most recent first)
    races_queryset = races_queryset.select_related('athlete', 'result').order_by('-date')
    
    # Pagination
    paginator = Paginator(races_queryset, 25)  # Show 25 races per page
    page_number = request.GET.get('page')
    races = paginator.get_page(page_number)
    
    # Calculate statistics (excluding current coach's races)
    coach_excluded_races = Race.objects.exclude(
        athlete__username=request.user.username
    ).exclude(
        athlete__email=request.user.email
    )
    
    upcoming_count = coach_excluded_races.filter(date__gte=today).count()
    completed_count = coach_excluded_races.filter(
        date__lt=today,
        result__isnull=False
    ).count()
    past_no_results_count = coach_excluded_races.filter(
        date__lt=today,
        result__isnull=True
    ).count()
    
    # Get all athletes except the current coach for filter dropdown
    all_athletes = User.objects.exclude(
        username=request.user.username
    ).exclude(
        email=request.user.email
    ).filter(
        id__in=coach_excluded_races.values_list('athlete_id', flat=True).distinct()
    ).order_by('first_name', 'last_name')
    
    total_athletes = all_athletes.count()
    
    # Get sport choices for filter dropdown
    sport_choices = getattr(Race, 'SPORT_CHOICES', [])
    
    context = {
        'races': races,
        'athletes': all_athletes,
        'sport_choices': sport_choices,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'past_no_results_count': past_no_results_count,
        'total_athletes': total_athletes,
        'is_paginated': races.has_other_pages(),
        'page_obj': races,
    }
    
    return render(request, 'race_events/coach_race_list.html', context)


@login_required
def race_create(request):
    """Create new race with proper error handling."""
    if request.method == 'POST':
        form = RaceForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                race = form.save(commit=False)
                race.athlete = request.user
                
                # Handle goal time logic
                goal_hours = request.POST.get('goal_hours', '') or '0'
                goal_minutes = request.POST.get('goal_minutes', '') or '0'
                goal_seconds = request.POST.get('goal_seconds', '') or '0'
                
                if goal_minutes != '0':
                    race.goal_time = f"{goal_hours}:{goal_minutes.zfill(2)}:{goal_seconds.zfill(2)}"
                
                race.save()
                
                # Log race creation
                log_user_action(logger, request.user, "created race", f"Race: {race.title}")
                
                UserMessages.success(
                    request, 
                    f'Race "{race.title}" created successfully!',
                    f"Race created: {race.title} by {request.user.username}"
                )
                
                return redirect('dashboard')
                
            except Exception as e:
                log_error(logger, "Error creating race", e, 
                         user=request.user.username, form_data=str(form.cleaned_data))
                UserMessages.error(
                    request,
                    "Unable to save your race. Please try again.",
                    "Race creation failed"
                )
        else:
            # Form validation failed
            log_warning(logger, "Race form validation failed", 
                       user=request.user.username, errors=str(form.errors))
            UserMessages.error(request, "Please correct the errors below and try again.")
    
    else:
        form = RaceForm(user=request.user)
        
        if 'date' in request.GET:
            form.fields['date'].initial = request.GET['date']
    
    return render(request, 'race_events/race_form.html', {
        'form': form,
        'title': 'Add New Race'
    })


@login_required
def race_detail(request, race_id):
    """View race details."""
    race = get_object_or_404(Race, id=race_id)
    
    # For now, allow access based on view mode or if it's their own race
    current_view = get_current_view_mode(request)
    if current_view != 'coach' and race.athlete != request.user:
        messages.error(request, 'You can only view your own races.')
        return redirect('race_events:race_list')
    
    return render(request, 'race_events/race_detail.html', {'race': race})


@login_required
def race_edit(request, race_id):
    """Edit race."""
    race = get_object_or_404(Race, id=race_id)
    
    # Check permissions based on view mode
    current_view = get_current_view_mode(request)
    if current_view != 'coach' and race.athlete != request.user:
        messages.error(request, 'You can only edit your own races.')
        return redirect('race_events:race_list')
    
    # Parse existing goal time into components for display
    goal_hours = goal_minutes = goal_seconds = ''
    if race.goal_time:
        time_parts = race.goal_time.split(':')
        goal_hours = time_parts[0] if len(time_parts) > 0 else ''
        goal_minutes = time_parts[1] if len(time_parts) > 1 else ''
        goal_seconds = time_parts[2] if len(time_parts) > 2 else ''
    
    if request.method == 'POST':
        form = RaceForm(request.POST, instance=race)
        if form.is_valid():
            updated_race = form.save(commit=False)
            
            # Handle separate goal time fields
            goal_hours = request.POST.get('goal_hours', '') or '0'
            goal_minutes = request.POST.get('goal_minutes', '') or '0' 
            goal_seconds = request.POST.get('goal_seconds', '') or '0'
            
            # Only set goal_time if at least minutes is provided
            if goal_minutes != '0':
                updated_race.goal_time = f"{goal_hours}:{goal_minutes.zfill(2)}:{goal_seconds.zfill(2)}"
            else:
                updated_race.goal_time = ''
            
            updated_race.save()
            messages.success(request, f'Race "{updated_race.title}" updated successfully!')
            return redirect('race_events:race_list')
    else:
        form = RaceForm(instance=race)
    
    context = {
        'form': form,
        'race': race,
        'title': f'Edit Race: {race.title}',
        'goal_hours': goal_hours,
        'goal_minutes': goal_minutes,
        'goal_seconds': goal_seconds,
    }
    return render(request, 'race_events/race_form.html', context)


@login_required
def race_delete(request, race_id):
    """Delete race."""
    race = get_object_or_404(Race, id=race_id)
    
    # Check permissions based on view mode
    current_view = get_current_view_mode(request)
    if current_view != 'coach' and race.athlete != request.user:
        messages.error(request, 'You can only delete your own races.')
        return redirect('race_events:race_list')
    
    if request.method == 'POST':
        race_name = race.title
        race.delete()
        messages.success(request, f'Race "{race_name}" deleted successfully!')
        return redirect('race_events:race_list')
    
    return render(request, 'race_events/race_confirm_delete.html', {'race': race})


@login_required
def race_result(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    
    # Check permissions based on view mode
    current_view = get_current_view_mode(request)
    if current_view != 'coach' and race.athlete != request.user:
        messages.error(request, 'You can only add results to your own races.')
        return redirect('race_events:race_list')
    
    # Get existing result if it exists
    try:
        result = race.result
        # Parse existing time into components
        if result and result.finish_time:
            time_parts = result.finish_time.split(':')
            existing_hours = time_parts[0] if len(time_parts) > 0 else '0'
            existing_minutes = time_parts[1] if len(time_parts) > 1 else '0'
            existing_seconds = time_parts[2] if len(time_parts) > 2 else '0'
        else:
            existing_hours = existing_minutes = existing_seconds = ''
    except RaceResult.DoesNotExist:
        result = None
        existing_hours = existing_minutes = existing_seconds = ''
    
    if request.method == 'POST':
        # Get form data
        overall_position = request.POST.get('overall_position', '') or None
        category_position = request.POST.get('category_position', '') or None
        total_participants = request.POST.get('total_participants', '') or None
        satisfaction = request.POST.get('satisfaction', '') or None
        race_report = request.POST.get('race_report', '').strip()
        
        # Finished time
        hours = request.POST.get('hours', '') or '0'
        minutes = request.POST.get('minutes', '')
        seconds = request.POST.get('seconds', '') or '0'

        # Validate required fields
        if not hours or not minutes or not seconds:
            messages.error(request, 'Please fill in hours, minutes, and seconds.')
            return render(request, 'race_events/race_result.html', {'race': race})
        
        finish_time = f"{hours}:{minutes.zfill(2)}:{seconds.zfill(2)}"
        
        # Create or update result
        if result:
            # Update existing result
            result.finish_time = finish_time
            result.overall_position = overall_position
            result.category_position = category_position
            result.total_participants = total_participants
            result.satisfaction = satisfaction
            result.race_report = race_report
            result.save()
            messages.success(request, f'Results for "{race.title}" updated successfully!')
        else:
            # Create new result
            result = RaceResult.objects.create(
                race=race,
                finish_time=finish_time,
                overall_position=overall_position,
                category_position=category_position,
                total_participants=total_participants,
                satisfaction=satisfaction,
                race_report=race_report
            )
            messages.success(request, f'Results for "{race.title}" saved successfully!')
        
        return redirect('race_events:race_list')
    
    context = {
        'race': race,
        'existing_hours': existing_hours,
        'existing_minutes': existing_minutes,
        'existing_seconds': existing_seconds,
    }
    return render(request, 'race_events/race_result.html', context)
