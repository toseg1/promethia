"""
Forms for race_events app - FIXED with athlete field for saving.
"""
from django import forms
from django.contrib.auth.models import User
from .models import Race
from training_calendar.constants import SPORT_CHOICES, RACE_GOAL_CHOICES, STATUS_CHOICES


class RaceForm(forms.ModelForm):
    """Form for creating and editing races."""
    
    # Override fields to explicitly use constants
    sport = forms.ChoiceField(
        choices=SPORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    goal_type = forms.ChoiceField(
        choices=RACE_GOAL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        initial='planned',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add athlete field - CRITICAL for saving races!
        if user:
            # Set athlete to current user (races are personal)
            self.fields['athlete'] = forms.ModelChoiceField(
                queryset=User.objects.filter(id=user.id),
                initial=user,
                required=False,
                widget=forms.HiddenInput()  # Hidden because races are personal to the user
            )
        else:
            # Fallback - shouldn't happen in normal flow
            self.fields['athlete'] = forms.ModelChoiceField(
                queryset=User.objects.all(),
                empty_label="Select Athlete",
                widget=forms.Select(attrs={'class': 'form-control'})
            )

        # Add helpful labels
        self.fields['title'].label = "Race Name"
        self.fields['sport'].label = "Sport Type"  
        self.fields['start_time'].label = "Start Time"
        self.fields['goal_type'].label = "Goal Type"
        self.fields['description'].label = "Race Description"
        self.fields['status'].label = "Status"
    
    class Meta:
        model = Race
        fields = [
            'athlete',       # CRITICAL: Required for saving
            'title', 'sport', 'date', 'start_time', 'location', 'venue',
            'distance', 'goal_time', 'goal_type', 'description', 'status'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Paris Marathon 2025',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Paris, France',
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., City Marathon Association',
            }),
            'distance': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 42.2km, Sprint, Half',
            }),
            'goal_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 3:30:00',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Race strategy, goals, or special notes...',
            }),
        }
        
