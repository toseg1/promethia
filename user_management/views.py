"""
User management views for dashboard, profiles, and relationships.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from datetime import datetime, timedelta, timezone
from .forms import SignUpForm, ProfileForm
from .models import Profile, CoachAthleteRelationship
from training_sessions.models import TrainingSession
from django.http import JsonResponse
from race_events.models import Race
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.views import PasswordResetView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import threading
from training_calendar.utils.logging_helpers import get_logger, log_error, log_warning, log_info, log_user_action
from training_calendar.utils.messages import UserMessages
from django.contrib.auth import authenticate, login as auth_login
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm 
from .forms import CustomLoginForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .forms import CustomPasswordResetForm
from django.contrib.auth.views import PasswordResetView
import cloudinary.uploader
import os

logger = get_logger('user_management')

def signup(request):
    """User registration with comprehensive error handling."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        # Log registration attempt
        email = request.POST.get('email', 'unknown')
        username = request.POST.get('username', 'unknown')
        log_info(logger, f"Registration attempt", username=username, email=email)
        
        if form.is_valid():
            try:
                # Create user
                user = form.save()
                
                # Set role on profile
                user.profile.role = form.cleaned_data['role']
                user.profile.save()
                
                # Log successful registration
                log_user_action(logger, user, "registered", f"Role: {user.profile.role}")
                
                # Login user
                auth_login(request, user)
                
                UserMessages.success(
                    request, 
                    'Account created successfully! Welcome to Promethia!',
                    f"New user registered: {user.username}"
                )
                
                return redirect('dashboard')
                
            except Exception as e:
                log_error(logger, "Error during user registration", e, 
                         username=username, email=email)
                UserMessages.error(
                    request,
                    "An error occurred during registration. Please try again.",
                    f"Registration error for {username}"
                )
        else:
            # Form validation failed - errors are already in form.errors
            # The template will display them automatically
            log_warning(logger, "Registration failed - form validation errors", 
                       username=username, form_errors=str(form.errors))
            
            # Add a general error message
            UserMessages.error(request, "Please correct the errors below and try again.")
    
    else:
        form = SignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def upload_avatar(request):
    """Upload avatar to Cloudinary and save URL to profile."""
    
    if request.method == 'POST':
        avatar_file = request.FILES.get('avatar')
        
        if not avatar_file:
            return JsonResponse({'success': False, 'error': 'No file provided'})
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'Invalid file type'})
        
        # Validate file size (max 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'File too large'})
        
        try:
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                avatar_file,
                folder="user_avatars",
                public_id=f"user_{request.user.id}",
                overwrite=True,
                resource_type="image",
                transformation=[
                    {'width': 300, 'height': 300, 'crop': 'fill'},
                    {'quality': 'auto'},
                    {'fetch_format': 'auto'}
                ]
            )
            
            # Save URL to user profile
            request.user.profile.avatar_url = upload_result['secure_url']
            request.user.profile.save()
            
        
            return JsonResponse({
                'success': True, 
                'url': upload_result['secure_url']
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def remove_avatar(request):
    """Remove avatar from Cloudinary and profile."""
    if request.method == 'POST':
        try:
            # Delete from Cloudinary if URL exists
            if request.user.profile.avatar_url:
                public_id = f"user_avatars/user_{request.user.id}"
                cloudinary.uploader.destroy(public_id)
            
            # Remove URL from profile
            request.user.profile.avatar_url = None
            request.user.profile.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required
def profile_edit(request):
    """Edit user profile."""
    if request.method == 'POST':
        # Handle picture removal
        if request.POST.get('remove_picture') == 'true':
            if request.user.profile.profile_picture:
                request.user.profile.profile_picture.delete(save=False)
                request.user.profile.profile_picture = None
                request.user.profile.save()
                messages.success(request, 'Profile picture removed successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'success': True})
            return redirect('profile_edit')
        
        # Handle normal form submission
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'success': True})
            
            return redirect('profile_edit')  # Stay on profile page
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'user_management/profile_edit.html', {'form': form})


@login_required
def add_athlete(request):
    """Add athlete by email (for coaches)."""
    
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            from django.contrib.auth.models import User
            athlete_user = User.objects.get(email=email, profile__role='athlete')
            
            # Check if relationship already exists
            existing = CoachAthleteRelationship.objects.filter(
                coach=request.user,
                athlete=athlete_user
            ).first()
            
            if existing:
                messages.warning(request, 'You already have a relationship with this athlete.')
            else:
                CoachAthleteRelationship.objects.create(
                    coach=request.user,
                    athlete=athlete_user,
                    status='pending'
                )
                messages.success(request, f'Request sent to {athlete_user.get_full_name()}!')
            
        except User.DoesNotExist:
            messages.error(request, 'No athlete found with this email address.')
    
    return render(request, 'user_management/add_athlete.html')


@login_required
def accept_coach(request, relationship_id):
    """Accept coach request (for athletes)."""
    relationship = get_object_or_404(
        CoachAthleteRelationship,
        id=relationship_id,
        athlete=request.user,
        status='pending'
    )
    
    relationship.accept()
    messages.success(request, f'You are now being coached by {relationship.coach.get_full_name()}!')
    return redirect('dashboard')  # ← This return was missing!

@login_required
def decline_coach(request, relationship_id):
    """Decline coach request (for athletes)."""
    relationship = get_object_or_404(
        CoachAthleteRelationship,
        id=relationship_id,
        athlete=request.user,
        status='pending'
    )
    
    coach_name = relationship.coach.get_full_name()
    relationship.delete()  # Remove the relationship entirely
    messages.success(request, f'Coach request from {coach_name} declined.')
    return redirect('dashboard')


@login_required
def switch_view(request):
    """Switch between athlete and coach views with smart redirection."""
    if request.method == 'POST':
        view_mode = request.POST.get('view_mode')
        if view_mode in ['athlete', 'coach']:
            # Clear any existing messages
            storage = messages.get_messages(request)
            storage.used = True
            
            # Store in session
            request.session['view_mode'] = view_mode
            request.session.modified = True  # Ensure session is saved
            
            # Get current page info
            referer = request.META.get('HTTP_REFERER', '')
            
            # Smart redirect logic
            redirect_url = None
            
            # If on any calendar page, redirect to appropriate calendar
            if '/calendar/' in referer:
                if view_mode == 'coach':
                    redirect_url = reverse('calendar_management:coach_view')
                else:
                    redirect_url = reverse('calendar_management:view')
            # If on races page, stay on races
            elif '/races/' in referer or '/race/' in referer:
                redirect_url = reverse('race_events:race_list')
            # If on profile page, stay on profil
            elif '/profile/edit/' in referer:
                redirect_url = reverse('profile_edit')
            # If on MAS page, stay on MAS
            elif '/vma-calculator/' in referer:
                redirect_url = reverse('vma_calculator')
            # Default to dashboard
            else:
                redirect_url = reverse('dashboard')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'view_mode': view_mode,
                    'redirect_url': redirect_url
                })
            
            return redirect(redirect_url)
    
    return redirect('dashboard')

def get_current_view_mode(request):
    """Get the current view mode from session or user's default role."""
    # Check session first
    session_view = request.session.get('view_mode')
    if session_view in ['athlete', 'coach']:
        return session_view
    
    # Default to user's role
    return request.user.profile.role

@login_required
def dashboard(request):
    """Main dashboard view with role switching capability and athlete selection."""
    user = request.user
    current_view = get_current_view_mode(request)
    
    # Get the selected athlete parameter from URL (for coach view)
    selected_athlete_id = request.GET.get('athlete', 'all')
    selected_athlete = None
    
    # Get upcoming sessions for this week
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    context = {
        'current_view': current_view,
        'user_role': user.profile.role,
        'selected_athlete_id': selected_athlete_id,
        'selected_athlete': None,
    }
    
    if current_view == 'athlete':
        # ATHLETE DASHBOARD (your existing logic)
        upcoming_sessions = TrainingSession.objects.filter(
            athlete=user,
            date__range=[today, week_end],
            status='planned'
        ).order_by('date', 'start_time')
        
        my_coaches = CoachAthleteRelationship.objects.filter(
            athlete=user,
            status='active'
        )
        
        pending_requests = CoachAthleteRelationship.objects.filter(
            athlete=user,
            status='pending'
        )
        
        # Get upcoming races for this athlete
        upcoming_races = Race.objects.filter(
            athlete=user,
            date__gte=datetime.now().date()
        ).order_by('date')
        
        # ADD THIS: Calculate completion rate for athlete (last 30 days)
        thirty_days_ago = today - timedelta(days=30)
        athlete_total_sessions = TrainingSession.objects.filter(
            athlete=user,
            date__gte=thirty_days_ago,
            date__lt=today
        )
        athlete_completed_sessions = athlete_total_sessions.filter(status='completed')
        
        session_completion_rate = 0
        if athlete_total_sessions.count() > 0:
            session_completion_rate = (athlete_completed_sessions.count() / athlete_total_sessions.count()) * 100
        
        context.update({
            'page_title': 'Athlete Dashboard',
            'upcoming_sessions': upcoming_sessions,
            'my_coaches': my_coaches,
            'pending_requests': pending_requests,
            'upcoming_races': upcoming_races,
            'session_completion_rate': session_completion_rate,  # ADD THIS LINE
        })
        
    else:  # Coach view
        # Get all coached athletes
        my_athletes = CoachAthleteRelationship.objects.filter(
            coach=user,
            status='active'
        )
        athlete_users = [rel.athlete for rel in my_athletes]
        
        context.update({
            'page_title': 'Coach Dashboard',
            'my_athletes': athlete_users,  # Pass the User objects for the dropdown
            'athlete_relationships': my_athletes,  # Keep relationships if needed
        })
        
        # Handle athlete selection
        if selected_athlete_id != 'all' and selected_athlete_id:
            try:
                selected_athlete = next(
                    (athlete for athlete in athlete_users if str(athlete.id) == selected_athlete_id), 
                    None
                )
                
                if selected_athlete:
                    context['selected_athlete'] = selected_athlete
                    
                    # Get data for the SELECTED ATHLETE only
                    athlete_upcoming_sessions = TrainingSession.objects.filter(
                        athlete=selected_athlete,
                        date__gte=today
                    ).order_by('date', 'start_time')
                    
                    athlete_upcoming_races = Race.objects.filter(
                        athlete=selected_athlete,
                        date__gte=datetime.now().date()
                    ).order_by('date')
                    
                    # Calculate completion rate for this athlete (last 30 days)
                    thirty_days_ago = today - timedelta(days=30)
                    total_sessions = TrainingSession.objects.filter(
                        athlete=selected_athlete,
                        date__gte=thirty_days_ago,
                        date__lt=today
                    )
                    completed_sessions = total_sessions.filter(status='completed')
                    
                    athlete_completion_rate = 0
                    if total_sessions.count() > 0:
                        athlete_completion_rate = (completed_sessions.count() / total_sessions.count()) * 100
                    
                    context.update({
                        'athlete_upcoming_sessions': athlete_upcoming_sessions,
                        'athlete_upcoming_races': athlete_upcoming_races,
                        'athlete_completion_rate': athlete_completion_rate,
                    })
                else:
                    # Invalid athlete ID, fall back to 'all'
                    selected_athlete_id = 'all'
                    context['selected_athlete_id'] = 'all'
                    
            except (ValueError, TypeError):
                # Invalid athlete ID format, fall back to 'all'
                selected_athlete_id = 'all'
                context['selected_athlete_id'] = 'all'
        
        if selected_athlete_id == 'all':
            # COACH OVERVIEW - All athletes data (your existing logic + enhancements)
            upcoming_sessions = TrainingSession.objects.filter(
                athlete__in=athlete_users,
                date__range=[today, week_end]
            ).order_by('date', 'start_time')
            
            # Get upcoming races for all coached athletes
            upcoming_races = Race.objects.filter(
                athlete__in=athlete_users,
                date__gte=datetime.now().date()
            ).order_by('date')
            
            # Calculate metrics for the overview widgets
            total_upcoming_sessions = TrainingSession.objects.filter(
                athlete__in=athlete_users,
                date__gte=today
            ).count()
            
            total_upcoming_races = Race.objects.filter(
                athlete__in=athlete_users,
                date__gte=datetime.now().date()
            ).count()
            
            # Calculate overall completion rate (last 30 days)
            thirty_days_ago = today - timedelta(days=30)
            total_sessions_all = TrainingSession.objects.filter(
                athlete__in=athlete_users,
                date__gte=thirty_days_ago,
                date__lt=today
            )

            total_sessions_count = 0
            total_completed_count = 0

            for athlete in athlete_users:
                athlete_sessions = TrainingSession.objects.filter(
                    athlete=athlete,
                    date__gte=thirty_days_ago,
                    date__lt=today
                )
                athlete_completed = athlete_sessions.filter(status='completed')
                
                athlete_total = athlete_sessions.count()
                athlete_comp = athlete_completed.count()
                
                total_sessions_count += athlete_total
                total_completed_count += athlete_comp
            

            # Calculate the rate
            session_completion_rate = 0
            if total_sessions_count > 0:
                session_completion_rate = (total_completed_count / total_sessions_count) * 100

            
            
            # Add completion rates to each athlete for the summary table
            for athlete in athlete_users:
                athlete_total = TrainingSession.objects.filter(
                    athlete=athlete,
                    date__gte=thirty_days_ago,
                    date__lt=today
                )
                athlete_completed = athlete_total.filter(status='completed')
                
                athlete.completion_rate = 0
                if athlete_total.count() > 0:
                    athlete.completion_rate = (athlete_completed.count() / athlete_total.count()) * 100
                
                # Add upcoming counts for each athlete
                athlete.upcoming_sessions_count = TrainingSession.objects.filter(
                    athlete=athlete,
                    date__gte=today
                ).count()
                
                athlete.upcoming_races_count = Race.objects.filter(
                    athlete=athlete,
                    date__gte=datetime.now().date()
                ).count()
            
            # Get all upcoming events for the events table
            all_upcoming_events = get_all_upcoming_events_for_coach(athlete_users)
            
            # Get recent activities
            recent_activities = get_recent_activities_for_coach(athlete_users)
            
            context.update({
                'upcoming_sessions': upcoming_sessions,
                'upcoming_races': upcoming_races,
                'total_upcoming_sessions': total_upcoming_sessions,
                'total_upcoming_races': total_upcoming_races,
                'session_completion_rate': session_completion_rate,
                'active_programs': len(recent_activities),  # You can implement this based on your program model
                'all_upcoming_events': all_upcoming_events,
                'recent_activities': recent_activities,
            })
        
        # Add coach-specific context (replace the missing function)
        pending_coach_requests = CoachAthleteRelationship.objects.filter(
            coach=user,
            status='pending'
        ).count()
        
        context.update({
            'pending_coach_requests': pending_coach_requests,
        })
    
    return render(request, 'user_management/dashboard.html', context)


def get_all_upcoming_events_for_coach(athlete_users):
    """Get combined upcoming events (sessions + races) for all athletes"""
    from datetime import datetime
    
    events = []
    
    # Get upcoming sessions
    upcoming_sessions = TrainingSession.objects.filter(
        athlete__in=athlete_users,
        date__gte=datetime.now().date()
    ).select_related('athlete').order_by('date', 'start_time')[:15]
    
    for session in upcoming_sessions:
        events.append({
            'date': session.date,
            'athlete_name': session.athlete.get_full_name(),
            'type': 'Training Session',
            'type_icon': 'dumbbell',
            'title': session.title if hasattr(session, 'title') else 'Training Session',
            'description': session.description if hasattr(session, 'description') else '',
            'status': session.get_status_display() if hasattr(session, 'get_status_display') else session.status,
            'status_color': 'primary' if session.status == 'planned' else 'success',
            'object_id': session.id,  # Add the actual object ID
            'object': session,  # Keep reference to the object if needed
            'sport': session.sport
        })
    
    # Get upcoming races
    upcoming_races = Race.objects.filter(
        athlete__in=athlete_users,
        date__gte=datetime.now().date()
    ).select_related('athlete').order_by('date')[:15]
    
    for race in upcoming_races:
        events.append({
            'date': race.date,
            'athlete_name': race.athlete.get_full_name(),
            'type': 'Race',
            'type_icon': 'trophy',
            'title': race.title,
            'description': f'{race.distance}' if hasattr(race, 'location') else '',
            'location': race.location,
            'status': 'Scheduled',
            'status_color': 'warning',
            'object_id': race.id,  # Add the actual object ID
            'object': race,  # Keep reference to the object if needed
            'sport': race.sport
        })
    
    # Sort all events by date
    events.sort(key=lambda x: x['date'])
    
    return events[:15]


def get_recent_activities_for_coach(athlete_users):
    """Get all recent activities from coached athletes (last 3 days)"""
    from datetime import datetime, timedelta
    from django.utils import timezone  # FIXED: Import Django timezone
    
    activities = []
    recent_date = timezone.now().date() - timedelta(days=3)  # FIXED: Use timezone.now()
    recent_datetime = timezone.now() - timedelta(days=3)  # FIXED: Use timezone.now()
    
    # 1. Recently CREATED training sessions
    try:
        created_sessions = TrainingSession.objects.filter(
            athlete__in=athlete_users,
            created_at__gte=recent_datetime
        ).select_related('athlete').order_by('-created_at')[:20]
        
        for session in created_sessions:
            activities.append({
                'timestamp': session.created_at,
                'date': session.created_at.date(),
                'start_time': session.created_at.time(),
                'athlete_name': session.athlete.get_full_name(),
                'description': f'Added new training session: {session.title if hasattr(session, "title") else "Training Session"}',
                'icon': 'plus-circle',
                'color': 'primary',
                'type': 'session_created'
            })
    except (AttributeError, FieldError):
        pass  # created_at field might not exist
    
    # 2. Recently COMPLETED training sessions
    try:
        completed_sessions = TrainingSession.objects.filter(
            athlete__in=athlete_users,
            date__gte=recent_date,
            status='completed'
        ).select_related('athlete').order_by('-date')[:20]
        
        for session in completed_sessions:
            # FIXED: Create timezone-aware datetime for sorting
            session_datetime = timezone.make_aware(
                datetime.combine(
                    session.date, 
                    session.start_time if hasattr(session, 'start_time') and session.time else datetime.min.time()
                )
            ) if hasattr(session, 'time') else timezone.now()
            
            activities.append({
                'timestamp': session_datetime,
                'date': session.date,
                'start_time': session.start_time if hasattr(session, 'start_time') else timezone.now().time(),
                'athlete_name': session.athlete.get_full_name(),
                'description': f'Completed training session: {session.title if hasattr(session, "title") else "Training Session"}',
                'icon': 'check-circle',
                'color': 'success',
                'type': 'session_completed'
            })
    except (AttributeError, FieldError):
        pass
    
    # 3. Recently CREATED races
    try:
        from race_events.models import Race
        created_races = Race.objects.filter(
            athlete__in=athlete_users,
            created_at__gte=recent_datetime
        ).select_related('athlete').order_by('-created_at')[:20]
        
        for race in created_races:
            activities.append({
                'timestamp': race.created_at,
                'date': race.created_at.date(),
                'start_time': race.created_at.time(),
                'athlete_name': race.athlete.get_full_name(),
                'description': f'Registered for race: {race.title}',
                'icon': 'trophy',
                'color': 'warning',
                'type': 'race_created'
            })
    except (ImportError, AttributeError, FieldError):
        pass
    
    # 4. Recently CREATED custom events
    try:
        from calendar_management.models import CustomEvent
        created_events = CustomEvent.objects.filter(
            user__in=athlete_users,
            created_at__gte=recent_datetime
        ).select_related('user').order_by('-created_at')[:20]
        
        for event in created_events:
            activities.append({
                'timestamp': event.created_at,
                'date': event.created_at.date(),
                'start_time': event.created_at.time(),
                'athlete_name': event.user.get_full_name(),
                'description': f'Added custom event: {event.title if hasattr(event, "title") else "Custom Event"}',
                'icon': 'star',
                'color': 'info',
                'type': 'custom_event_created'
            })
    except (ImportError, AttributeError, FieldError):
        pass
    
    # 5. Profile updates
    try:
        from user_management.models import Profile
        updated_profiles = Profile.objects.filter(
            user__in=athlete_users,
            updated_at__gte=recent_datetime
        ).select_related('user').order_by('-updated_at')[:10]
        
        for profile in updated_profiles:
            updates = []
            if hasattr(profile, 'vma') and profile.vma:
                updates.append(f'VMA: {profile.vma} km/h')
            if hasattr(profile, 'ftp') and profile.ftp:
                updates.append(f'FTP: {profile.ftp} W')
            if hasattr(profile, 'css') and profile.css:
                updates.append(f'CSS: {profile.css}/100m')
            
            if updates:
                activities.append({
                    'timestamp': profile.updated_at,
                    'date': profile.updated_at.date(),
                    'start_time': profile.updated_at.time(),
                    'athlete_name': profile.user.get_full_name(),
                    'description': f'Updated performance metrics: {", ".join(updates)}',
                    'icon': 'user-edit',
                    'color': 'info',
                    'type': 'profile_updated'
                })
    except (ImportError, AttributeError, FieldError):
        pass
    
    # 6. Recently CANCELLED sessions
    try:
        cancelled_sessions = TrainingSession.objects.filter(
            athlete__in=athlete_users,
            updated_at__gte=recent_datetime,
            status='cancelled'
        ).select_related('athlete').order_by('-updated_at')[:10]
        
        for session in cancelled_sessions:
            activities.append({
                'timestamp': session.updated_at,
                'date': session.updated_at.date(),
                'start_time': session.updated_at.time(),
                'athlete_name': session.athlete.get_full_name(),
                'description': f'Cancelled training session: {session.title if hasattr(session, "title") else "Training Session"}',
                'icon': 'times-circle',
                'color': 'danger',
                'type': 'session_cancelled'
            })
    except (AttributeError, FieldError):
        pass
    
    # Sort all activities by timestamp (most recent first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Return count and list (limited to 15 most recent)
    final_activities = activities[:15]
    return final_activities


@login_required
def athlete_detail(request, athlete_id):
    """
    Detailed view of a specific athlete for coaches
    """
    # Verify that the current user is a coach of this athlete
    athlete = get_object_or_404(User, id=athlete_id)
    
    # Check if current user coaches this athlete
    relationship = get_object_or_404(
        CoachAthleteRelationship,
        coach=request.user,
        athlete=athlete,
        status='active'
    )
    
    # Get athlete's detailed information
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Training sessions data
    upcoming_sessions = TrainingSession.objects.filter(
        athlete=athlete,
        date__gte=today
    ).order_by('date', 'start_time')
    
    recent_sessions = TrainingSession.objects.filter(
        athlete=athlete,
        date__gte=thirty_days_ago,
        date__lt=today
    ).order_by('-date', '-start_time')[:10]
    
    # Races data
    upcoming_races = Race.objects.filter(
        athlete=athlete,
        date__gte=today
    ).order_by('date')
    
    past_races = Race.objects.filter(
        athlete=athlete,
        date__lt=today
    ).order_by('-date')[:5]
    
    # Performance metrics
    total_sessions_30d = TrainingSession.objects.filter(
        athlete=athlete,
        date__gte=thirty_days_ago,
        date__lt=today
    )
    completed_sessions_30d = total_sessions_30d.filter(status='completed')
    
    completion_rate = 0
    if total_sessions_30d.count() > 0:
        completion_rate = (completed_sessions_30d.count() / total_sessions_30d.count()) * 100
    
    # Training consistency (sessions per week)
    weeks_in_period = 4  # 30 days ≈ 4 weeks
    avg_sessions_per_week = total_sessions_30d.count() / weeks_in_period if weeks_in_period > 0 else 0
    
    context = {
        'athlete': athlete,
        'relationship': relationship,
        'upcoming_sessions': upcoming_sessions,
        'recent_sessions': recent_sessions,
        'upcoming_races': upcoming_races,
        'past_races': past_races,
        'completion_rate': completion_rate,
        'total_sessions_30d': total_sessions_30d.count(),
        'completed_sessions_30d': completed_sessions_30d.count(),
        'avg_sessions_per_week': round(avg_sessions_per_week, 1),
        'page_title': f'{athlete.get_full_name()} - Athlete Detail',
    }
    
    return render(request, 'user_management/athlete_detail.html', context)


@login_required
@require_POST
def remove_athlete(request, athlete_id):
    """
    Remove coach-athlete relationship
    """
    try:
        # Get the athlete
        athlete = get_object_or_404(User, id=athlete_id)
        
        # Find and delete the relationship
        relationship = get_object_or_404(
            CoachAthleteRelationship,
            coach=request.user,
            athlete=athlete,
            status='active'
        )
        
        # Store athlete name for the message
        athlete_name = athlete.get_full_name()
        
        # Delete the relationship
        relationship.delete()
        
        # If this is an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{athlete_name} has been removed from your coached athletes.'
            })
        
        # If regular request, add message and redirect
        messages.success(request, f'{athlete_name} has been removed from your coached athletes.')
        return redirect('dashboard')
        
    except CoachAthleteRelationship.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'You are not coaching this athlete.'
            }, status=404)
        
        messages.error(request, 'You are not coaching this athlete.')
        return redirect('dashboard')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
        messages.error(request, f'Error removing athlete: {str(e)}')
        return redirect('dashboard')
    
@login_required
def vma_calculator(request):
    """VMA Calculator view that respects current view mode"""
    
    # Get current view from session (same logic as other views)
    current_view = request.session.get('view_mode', 'athlete')
    
    # For coaches, they might have a selected athlete
    selected_athlete = None
    if current_view == 'athlete' and hasattr(request.user, 'coached_athletes'):
        # If coach is in athlete view, get the selected athlete from session
        selected_athlete_id = request.session.get('selected_athlete_id')
        if selected_athlete_id:
            try:
                selected_athlete = request.user.coached_athletes.get(id=selected_athlete_id)
            except:
                selected_athlete = None
    
    # Get user's VMA (either coach's own VMA or selected athlete's VMA)
    user_vma = None
    if current_view == 'coach':
        # Coach view - use coach's own VMA
        if hasattr(request.user, 'profile') and request.user.profile.vma:
            user_vma = request.user.profile.vma
    else:
        # Athlete view
        if selected_athlete:
            # Coach looking at athlete's data
            if hasattr(selected_athlete, 'profile') and selected_athlete.profile.vma:
                user_vma = selected_athlete.profile.vma
        else:
            # Regular athlete or coach looking at own data
            if hasattr(request.user, 'profile') and request.user.profile.vma:
                user_vma = request.user.profile.vma
    
    context = {
        'current_view': current_view,  # This is the key fix!
        'selected_athlete': selected_athlete,
        'user_vma': user_vma,
    }
    
    return render(request, 'user_management/vma_calculator.html', context)

@login_required
@require_POST
def remove_profile_picture(request):
    request.user.profile.profile_picture.delete(save=True)
    messages.success(request, "Profile picture removed.")
    return redirect('profile_edit')

def simple_password_reset(request):
    """Simple password reset with error for non-users and background email"""
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        
        if not email:
            messages.error(request, "Please enter an email address.")
            return render(request, 'registration/password_reset_form.html')
        
        # STEP 1: Check if user exists
        try:
            user = User.objects.get(email=email)
            
            # STEP 2: User exists - send email in background
            def send_reset_email():
                """Send the password reset email in background thread"""
                try:
                    
                    # Generate token
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    # Get domain
                    current_site = get_current_site(request)
                    domain = current_site.domain
                    protocol = 'https' if request.is_secure() else 'http'
                    
                    # Create reset URL
                    reset_url = f"{protocol}://{domain}/accounts/reset/{uid}/{token}/"
                    
                    # Email message
                    subject = "Reset your Promethia password"
                    message = f"""Hello {user.get_full_name() or user.username},

You requested a password reset for your Promethia Training Calendar account.

Click this link to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this password reset, please ignore this email.

Best regards,
The Promethia Team

---
This email was sent to {email} because you requested a password reset.
"""
                    
                    
                    # Send email
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            
            # Start email thread (NOT daemon so it completes)
            email_thread = threading.Thread(target=send_reset_email)
            email_thread.daemon = False  # Important: Let thread complete
            email_thread.start()
            
            return redirect('password_reset_done')
            
        except User.DoesNotExist:
            messages.error(
                request, 
                f"No account found with email {email}. Please register for a new account."
            )
            
            # Stay on the same page to show the error
            return render(request, 'registration/password_reset_form.html')
    
    # GET request - show the form
    return render(request, 'registration/password_reset_form.html')

def custom_login(request: HttpRequest) -> HttpResponse:
    """Custom login view with comprehensive error handling and logging."""
    
    # Redirect if already authenticated
    if request.user.is_authenticated:
        log_info(logger, f"Already authenticated user tried to access login", 
                user=request.user.username)
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        # Get credentials for logging (before validation)
        username = request.POST.get('username', 'unknown')
        
        # Log login attempt
        log_info(logger, "Login attempt", username=username, ip=request.META.get('REMOTE_ADDR'))
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    # Successful login
                    auth_login(request, user)
                    
                    # Log successful login
                    log_user_action(logger, user, "logged in", 
                                   f"IP: {request.META.get('REMOTE_ADDR')}")
                    
                    # Welcome message
                    UserMessages.success(
                        request, 
                        f"Welcome back, {user.get_full_name() or user.username}!",
                        f"Successful login: {user.username}"
                    )
                    
                    # Redirect to next page or dashboard
                    next_page = request.GET.get('next')
                    if next_page:
                        log_info(logger, f"Redirecting to requested page: {next_page}", 
                                user=user.username)
                        return redirect(next_page)
                    else:
                        return redirect('dashboard')
                
                else:
                    # Account is inactive
                    log_warning(logger, "Login failed - inactive account", 
                               username=username, ip=request.META.get('REMOTE_ADDR'))
                    UserMessages.error(
                        request,
                        "Your account has been deactivated. Please contact support for assistance.",
                        f"Inactive account login attempt: {username}"
                    )
            else:
                # Invalid credentials
                log_warning(logger, "Login failed - invalid credentials", 
                        username=username, ip=request.META.get('REMOTE_ADDR'))
                
                UserMessages.error(
                    request,
                    "Invalid username or password. Please check your credentials and try again.",
                    f"Invalid login attempt: {username}"
                )
        else:
            # Form validation failed
            log_warning(logger, "Login form validation failed", 
                       username=username, errors=str(form.errors))
            
            # Handle specific form errors
            if form.non_field_errors():
                # Django's AuthenticationForm puts credential errors in non_field_errors
                UserMessages.error(
                    request,
                    "Invalid username or password. Please check your credentials and try again."
                )
            else:
                # Other form errors (empty fields, etc.)
                UserMessages.error(
                    request,
                    "Please fill in all required fields."
                )
    
    else:
        # GET request - show login form
        form = AuthenticationForm()
        
        # Log if user came from a redirect (e.g., login required)
        next_page = request.GET.get('next')
        if next_page:
            log_info(logger, f"Login required for page: {next_page}")
            UserMessages.info(
                request,
                "Please log in to access that page."
            )
    
    return render(request, 'registration/login.html', {
        'form': form,
        'title': 'Log In'
    })


def custom_logout(request: HttpRequest) -> HttpResponse:
    """Custom logout view with logging."""
    
    if request.user.is_authenticated:
        username = request.user.username
        log_user_action(logger, request.user, "logged out", 
                       f"IP: {request.META.get('REMOTE_ADDR')}")
        
        logout(request)
        
        UserMessages.success(
            request,
            "You have been logged out successfully.",
            f"User logged out: {username}"
        )
    
    return redirect('custom_login')


class CustomLoginView(LoginView):
    """
    Custom login view using our CustomLoginForm.
    """
    form_class = CustomLoginForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')  # Change to your dashboard URL
    
    def form_invalid(self, form):
        """
        Handle form validation errors.
        """
        # Add any additional error handling here if needed
        return super().form_invalid(form)
    
    def form_valid(self, form):
        """
        Handle successful login.
        """
        messages.success(self.request, 'Welcome back! You have been logged in successfully.')
        return super().form_valid(form)
    

class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view with styled form and messages.
    MODIFIED: Now sends plain text emails instead of HTML
    """
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    
    # REMOVED: email_template_name = 'registration/password_reset_email.html'  # This was causing HTML emails
    # REMOVED: subject_template_name = 'registration/password_reset_subject.txt'
    
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        """
        Handle successful form submission with custom success message.
        MODIFIED: Now sends plain text email manually
        """
        # Get the email from the form
        email = form.cleaned_data['email']
        
        # Check if user exists
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            
            # Send plain text email manually
            self.send_plain_text_email(user, email)
            
            # Add success message
            messages.success(
                self.request,
                f'Password reset instructions have been sent to {email}. Please check your email.'
            )
            
            return redirect(self.success_url)
            
        except User.DoesNotExist:
            # Handle non-existent user (security: don't reveal if email exists)
            messages.success(
                self.request,
                f'If an account with {email} exists, password reset instructions have been sent.'
            )
            return redirect(self.success_url)
    
    def send_plain_text_email(self, user, email):
        """Send plain text password reset email"""
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.sites.shortcuts import get_current_site
        from django.core.mail import send_mail
        from django.conf import settings
        import threading
        
        def send_reset_email():
            try:
                
                # Generate token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Get domain
                current_site = get_current_site(self.request)
                domain = current_site.domain
                protocol = 'https' if self.request.is_secure() else 'http'
                
                # Create reset URL
                reset_url = f"{protocol}://{domain}/accounts/reset/{uid}/{token}/"
                
                # Plain text email message
                subject = "Reset your Promethia password"
                message = f"""Hello {user.get_full_name() or user.username},

You requested a password reset for your Promethia Training Calendar account.

Click this link to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this password reset, please ignore this email.

Best regards,
The Promethia Team

---
This email was sent to {email} because you requested a password reset.
"""
                
                
                # Send email
                result = send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        # Send email in background thread
        email_thread = threading.Thread(target=send_reset_email)
        email_thread.daemon = False
        email_thread.start()
    
    def form_invalid(self, form):
        """
        Handle form validation errors.
        """
        
        # Add error message for general form issues
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)
        
        return super().form_invalid(form)