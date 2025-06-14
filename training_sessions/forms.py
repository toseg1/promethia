"""
Forms for training sessions - FIXED with athlete field visible.
"""
from django import forms
from django.contrib.auth.models import User
from .models import TrainingSession
from user_management.models import CoachAthleteRelationship
from training_calendar.constants import SPORT_CHOICES, INTENSITY_CHOICES, STATUS_CHOICES


class TrainingSessionForm(forms.ModelForm):
    """Form for creating and editing training sessions."""
    
    # Override fields to explicitly use constants
    sport = forms.ChoiceField(
        choices=SPORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    intensity = forms.ChoiceField(
        choices=INTENSITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, athlete_choices=None, user=None, current_view=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # IMPORTANT: Athlete field logic - this was getting lost!
        if athlete_choices:
            athlete_ids = [choice[0] for choice in athlete_choices]
            
            if (user and current_view == 'athlete' and 
                hasattr(user, 'profile') and user.profile.role == 'coach' and 
                user.id not in athlete_ids):
                athlete_ids.append(user.id)
            
            self.fields['athlete'] = forms.ModelChoiceField(
                queryset=User.objects.filter(id__in=athlete_ids),
                empty_label=None,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        elif user:
            # For normal users, show athlete selection
            if current_view == 'athlete':
                if hasattr(user, 'profile') and user.profile.role == 'coach':
                    # Coach in athlete view - show themselves
                    self.fields['athlete'] = forms.ModelChoiceField(
                        queryset=User.objects.filter(id=user.id),
                        initial=user,
                        widget=forms.Select(attrs={'class': 'form-control'})  # CHANGED: was HiddenInput
                    )
                else:
                    # Regular athlete - show themselves
                    self.fields['athlete'] = forms.ModelChoiceField(
                        queryset=User.objects.filter(id=user.id),
                        initial=user,
                        widget=forms.Select(attrs={'class': 'form-control'})  # CHANGED: was HiddenInput
                    )
            else:
                # Coach view - show all coached athletes
                try:
                    coached_athletes = CoachAthleteRelationship.objects.filter(
                        coach=user, status='accepted'
                    ).values_list('athlete_id', flat=True)
                    
                    if coached_athletes:
                        self.fields['athlete'] = forms.ModelChoiceField(
                            queryset=User.objects.filter(id__in=coached_athletes),
                            empty_label="Select Athlete",
                            widget=forms.Select(attrs={'class': 'form-control'})
                        )
                    else:
                        # No coached athletes, show current user
                        self.fields['athlete'] = forms.ModelChoiceField(
                            queryset=User.objects.filter(id=user.id),
                            initial=user,
                            widget=forms.Select(attrs={'class': 'form-control'})
                        )
                except:
                    # Fallback - show current user
                    self.fields['athlete'] = forms.ModelChoiceField(
                        queryset=User.objects.filter(id=user.id),
                        initial=user,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
        else:
            # No user context - show all users (shouldn't happen in normal flow)
            self.fields['athlete'] = forms.ModelChoiceField(
                queryset=User.objects.all(),
                empty_label="Select Athlete",
                widget=forms.Select(attrs={'class': 'form-control'})
            )
    
    class Meta:
        model = TrainingSession
        fields = [
            'athlete',       # IMPORTANT: Must be first for proper display
            'title', 'sport', 'date', 'start_time',
            'duration_minutes', 'distance', 'intensity', 'description', 'status'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10K Tempo Run, Recovery Swim'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '60',
                'min': '1',
                'max': '600'
            }),
            'distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10.0',
                'step': '0.1',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Workout details, target zones, instructions...'
            }),
        }