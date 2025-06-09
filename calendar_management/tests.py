# calendar_management/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import CustomEvent
from .forms import CustomEventForm
from user_management.models import CoachAthleteRelationship


class CustomEventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_custom_event(self):
        """Test creating a custom event"""
        event = CustomEvent.objects.create(
            user=self.user,
            title='Test Event',
            note='Test note',
            color='#007bff',
            start_date=date.today(),
            end_date=date.today()
        )
        
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.user, self.user)
        self.assertFalse(event.is_multi_day)
        self.assertEqual(event.duration_days, 1)
    
    def test_multi_day_event(self):
        """Test multi-day event properties"""
        start_date = date.today()
        end_date = start_date + timedelta(days=3)
        
        event = CustomEvent.objects.create(
            user=self.user,
            title='Multi-day Event',
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertTrue(event.is_multi_day)
        self.assertEqual(event.duration_days, 4)
    
    def test_event_str_representation(self):
        """Test string representation of events"""
        # Single day event
        single_day_event = CustomEvent.objects.create(
            user=self.user,
            title='Single Day',
            start_date=date.today(),
            end_date=date.today()
        )
        
        self.assertIn('Single Day', str(single_day_event))
        self.assertIn(str(date.today()), str(single_day_event))
        
        # Multi-day event
        start_date = date.today()
        end_date = start_date + timedelta(days=2)
        
        multi_day_event = CustomEvent.objects.create(
            user=self.user,
            title='Multi Day',
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertIn('Multi Day', str(multi_day_event))
        self.assertIn(' - ', str(multi_day_event))


class CustomEventFormTest(TestCase):
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'title': 'Test Event',
            'note': 'Test note',
            'color': '#007bff',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=1)
        }
        
        form = CustomEventForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_date_range(self):
        """Test form with invalid date range"""
        form_data = {
            'title': 'Test Event',
            'start_date': date.today(),
            'end_date': date.today() - timedelta(days=1)  # End before start
        }
        
        form = CustomEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('End date cannot be before start date', str(form.errors))
    
    def test_long_duration_validation(self):
        """Test validation for very long events"""
        form_data = {
            'title': 'Long Event',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=400)  # Over 1 year
        }
        
        form = CustomEventForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_required_fields(self):
        """Test required field validation"""
        form = CustomEventForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)


class CalendarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.athlete = User.objects.create_user(
            username='athlete',
            email='athlete@example.com',
            password='testpass123'
        )
        self.coach = User.objects.create_user(
            username='coach',
            email='coach@example.com',
            password='testpass123'
        )
        
        # Create coach-athlete relationship
        CoachAthleteRelationship.objects.create(
            coach=self.coach,
            athlete=self.athlete,
            status='accepted'
        )
        
        # Create test events
        self.custom_event = CustomEvent.objects.create(
            user=self.athlete,
            title='Test Custom Event',
            start_date=date.today(),
            end_date=date.today()
        )
    
    def test_athlete_calendar_view(self):
        """Test athlete calendar view"""
        self.client.login(username='athlete', password='testpass123')
        
        # Set athlete view
        session = self.client.session
        session['current_view'] = 'athlete'
        session.save()
        
        response = self.client.get(reverse('calendar_management:view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Training Calendar')
        self.assertContains(response, 'Test Custom Event')
    
    def test_coach_calendar_view(self):
        """Test coach calendar view"""
        self.client.login(username='coach', password='testpass123')
        
        # Set coach view
        session = self.client.session
        session['current_view'] = 'coach'
        session.save()
        
        response = self.client.get(reverse('calendar_management:view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Athletes Calendar')
    
    def test_coach_specific_athlete_view(self):
        """Test coach viewing specific athlete"""
        self.client.login(username='coach', password='testpass123')
        
        # Set coach view
        session = self.client.session
        session['current_view'] = 'coach'
        session.save()
        
        response = self.client.get(
            reverse('calendar_management:view') + f'?athlete={self.athlete.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.athlete.get_full_name())
        self.assertContains(response, 'Test Custom Event')
    
    def test_week_view(self):
        """Test week view"""
        self.client.login(username='athlete', password='testpass123')
        
        response = self.client.get(
            reverse('calendar_management:view') + '?view=week'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Week of')
    
    def test_month_view(self):
        """Test month view (default)"""
        self.client.login(username='athlete', password='testpass123')
        
        response = self.client.get(reverse('calendar_management:view'))
        self.assertEqual(response.status_code, 200)
        # Should contain month navigation
        self.assertContains(response, 'chevron-left')
        self.assertContains(response, 'chevron-right')
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.get(reverse('calendar_management:view'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class CustomEventViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.custom_event = CustomEvent.objects.create(
            user=self.user,
            title='Test Event',
            start_date=date.today(),
            end_date=date.today()
        )
    
    def test_create_custom_event_get(self):
        """Test GET request to create custom event"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('calendar_management:create_custom_event'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Custom Event')
        self.assertContains(response, 'Event Title')
    
    def test_create_custom_event_post(self):
        """Test POST request to create custom event"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'title': 'New Test Event',
            'note': 'Test note',
            'color': '#28a745',
            'start_date': date.today() + timedelta(days=1),
            'end_date': date.today() + timedelta(days=1)
        }
        
        response = self.client.post(
            reverse('calendar_management:create_custom_event'),
            data=form_data
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check that event was created
        new_event = CustomEvent.objects.get(title='New Test Event')
        self.assertEqual(new_event.user, self.user)
        self.assertEqual(new_event.color, '#28a745')
    
    def test_edit_custom_event(self):
        """Test editing custom event"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('calendar_management:edit_custom_event', args=[self.custom_event.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Custom Event')
        self.assertContains(response, self.custom_event.title)
    
    def test_edit_custom_event_post(self):
        """Test POST request to edit custom event"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'title': 'Updated Event Title',
            'note': 'Updated note',
            'color': '#dc3545',
            'start_date': self.custom_event.start_date,
            'end_date': self.custom_event.end_date
        }
        
        response = self.client.post(
            reverse('calendar_management:edit_custom_event', args=[self.custom_event.id]),
            data=form_data
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Check that event was updated
        updated_event = CustomEvent.objects.get(id=self.custom_event.id)
        self.assertEqual(updated_event.title, 'Updated Event Title')
        self.assertEqual(updated_event.color, '#dc3545')
    
    def test_delete_custom_event(self):
        """Test deleting custom event"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('calendar_management:delete_custom_event', args=[self.custom_event.id])
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Check that event was deleted
        with self.assertRaises(CustomEvent.DoesNotExist):
            CustomEvent.objects.get(id=self.custom_event.id)
    
    def test_unauthorized_edit_attempt(self):
        """Test that users can't edit other users' events"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.login(username='otheruser', password='testpass123')
        
        response = self.client.get(
            reverse('calendar_management:edit_custom_event', args=[self.custom_event.id])
        )
        self.assertEqual(response.status_code, 404)  # Should not be found
    
    def test_unauthorized_delete_attempt(self):
        """Test that users can't delete other users' events"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.login(username='otheruser', password='testpass123')
        
        response = self.client.post(
            reverse('calendar_management:delete_custom_event', args=[self.custom_event.id])
        )
        self.assertEqual(response.status_code, 404)  # Should not be found


class CalendarAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.custom_event = CustomEvent.objects.create(
            user=self.user,
            title='API Test Event',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            color='#007bff'
        )
    
    def test_get_calendar_events_api(self):
        """Test API endpoint for getting calendar events"""
        self.client.login(username='testuser', password='testpass123')
        
        # Set athlete view
        session = self.client.session
        session['current_view'] = 'athlete'
        session.save()
        
        response = self.client.get(reverse('calendar_management:api_events'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('events', data)
        
        # Check that our custom event is in the response
        events = data['events']
        custom_events = [e for e in events if e['type'] == 'custom']
        self.assertEqual(len(custom_events), 1)
        self.assertEqual(custom_events[0]['title'], 'API Test Event')
    
    def test_api_with_date_filters(self):
        """Test API with date range filters"""
        self.client.login(username='testuser', password='testpass123')
        
        # Set athlete view
        session = self.client.session
        session['current_view'] = 'athlete'
        session.save()
        
        # Test month view
        today = date.today()
        response = self.client.get(
            reverse('calendar_management:api_events'),
            {
                'view': 'month',
                'year': today.year,
                'month': today.month
            }
        )
        self.assertEqual(response.status_code, 200)
        
        # Test week view
        response = self.client.get(
            reverse('calendar_management:api_events'),
            {
                'view': 'week',
                'week_start': today.isoformat()
            }
        )
        self.assertEqual(response.status_code, 200)
    
    def test_unauthenticated_api_access(self):
        """Test that API requires authentication"""
        response = self.client.get(reverse('calendar_management:api_events'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class CalendarTemplateTagsTest(TestCase):
    def test_month_name_filter(self):
        """Test month name template filter"""
        from .templatetags.calendar_extras import month_name
        
        self.assertEqual(month_name(1), 'January')
        self.assertEqual(month_name(12), 'December')
        self.assertEqual(month_name(0), '')  # Invalid month
        self.assertEqual(month_name('invalid'), '')  # Invalid input
    
    def test_add_days_filter(self):
        """Test add days template filter"""
        from .templatetags.calendar_extras import add_days
        
        test_date = date(2023, 1, 1)
        result = add_days(test_date, 5)
        expected = date(2023, 1, 6)
        self.assertEqual(result, expected)
        
        # Test with string date
        result = add_days('2023-01-01', 5)
        self.assertEqual(result, expected)
    
    def test_format_duration_filter(self):
        """Test duration formatting filter"""
        from .templatetags.calendar_extras import format_duration
        
        self.assertEqual(format_duration(30), '30m')
        self.assertEqual(format_duration(60), '1h')
        self.assertEqual(format_duration(90), '1h 30m')
        self.assertEqual(format_duration(120), '2h')
        self.assertEqual(format_duration('invalid'), '')
    
    def test_sport_icon_filter(self):
        """Test sport icon filter"""
        from .templatetags.calendar_extras import sport_icon
        
        self.assertEqual(sport_icon('running'), 'fas fa-running')
        self.assertEqual(sport_icon('cycling'), 'fas fa-bicycle')
        self.assertEqual(sport_icon('swimming'), 'fas fa-swimmer')
        self.assertEqual(sport_icon('unknown_sport'), 'fas fa-dumbbell')
    
    def test_sport_color_filter(self):
        """Test sport color filter"""
        from .templatetags.calendar_extras import sport_color
        
        self.assertEqual(sport_color('running'), '#28a745')
        self.assertEqual(sport_color('cycling'), '#007bff')
        self.assertEqual(sport_color('swimming'), '#17a2b8')
        self.assertEqual(sport_color('unknown_sport'), '#6c757d')


class CalendarIntegrationTest(TestCase):
    """Integration tests for calendar functionality"""
    
    def setUp(self):
        self.client = Client()
        self.athlete = User.objects.create_user(
            username='athlete',
            email='athlete@example.com',
            password='testpass123'
        )
        self.coach = User.objects.create_user(
            username='coach',
            email='coach@example.com',
            password='testpass123'
        )
        
        # Create profiles
        from user_management.models import UserProfile
        UserProfile.objects.create(user=self.athlete)
        UserProfile.objects.create(user=self.coach, is_coach=True)
        
        # Create coach-athlete relationship
        CoachAthleteRelationship.objects.create(
            coach=self.coach,
            athlete=self.athlete,
            status='accepted'
        )
    
    def test_complete_calendar_workflow(self):
        """Test complete workflow from athlete and coach perspectives"""
        
        # 1. Athlete creates custom event
        self.client.login(username='athlete', password='testpass123')
        
        # Set athlete view
        session = self.client.session
        session['current_view'] = 'athlete'
        session.save()
        
        # Create custom event
        form_data = {
            'title': 'Vacation',
            'note': 'Family vacation - no training',
            'color': '#ffc107',
            'start_date': date.today() + timedelta(days=5),
            'end_date': date.today() + timedelta(days=10)
        }
        
        response = self.client.post(
            reverse('calendar_management:create_custom_event'),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify event was created
        event = CustomEvent.objects.get(title='Vacation')
        self.assertEqual(event.user, self.athlete)
        
        # 2. Check that athlete can see the event in calendar
        response = self.client.get(reverse('calendar_management:view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vacation')
        
        # 3. Coach logs in and views athlete's calendar
        self.client.login(username='coach', password='testpass123')
        
        # Set coach view
        session = self.client.session
        session['current_view'] = 'coach'
        session.save()
        
        # View specific athlete's calendar
        response = self.client.get(
            reverse('calendar_management:view') + f'?athlete={self.athlete.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vacation')
        self.assertContains(response, self.athlete.get_full_name())
        
        # 4. Test API access from coach perspective
        response = self.client.get(
            reverse('calendar_management:api_events') + f'?athlete={self.athlete.id}'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        custom_events = [e for e in data['events'] if e['type'] == 'custom']
        self.assertEqual(len(custom_events), 1)
        self.assertEqual(custom_events[0]['title'], 'Vacation')
    
    def test_calendar_permissions(self):
        """Test calendar permission scenarios"""
        
        # Create another user not related to coach/athlete
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Athlete creates event
        self.client.login(username='athlete', password='testpass123')
        
        event = CustomEvent.objects.create(
            user=self.athlete,
            title='Private Event',
            start_date=date.today(),
            end_date=date.today()
        )
        
        # Other user logs in and tries to access athlete's event
        self.client.login(username='otheruser', password='testpass123')
        
        response = self.client.get(
            reverse('calendar_management:edit_custom_event', args=[event.id])
        )
        self.assertEqual(response.status_code, 404)  # Should not be accessible
        
        # Coach should be able to view (but not edit) athlete's events
        self.client.login(username='coach', password='testpass123')
        
        # Set coach view
        session = self.client.session
        session['current_view'] = 'coach'
        session.save()
        
        response = self.client.get(
            reverse('calendar_management:view') + f'?athlete={self.athlete.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Private Event')