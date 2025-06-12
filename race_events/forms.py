"""
Forms for race_events app - FIXED with standardized fields.
"""
from django import forms
from .models import Race
from training_calendar.constants import SPORT_CHOICES, RACE_GOAL_CHOICES, STATUS_CHOICES


class RaceForm(forms.ModelForm):
    """Form for creating and editing races - FIXED with standardized fields."""
    
    sport = forms.ChoiceField(
        choices=SPORT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'sportSelect'
        })
    )
    
    class Meta:
        model = Race
        fields = [
            'title',        # FIXED: was 'name'
            'sport',        # FIXED: was 'sport_type' 
            'date', 
            'start_time',   # FIXED: was 'time'
            'location', 
            'venue',
            'distance', 
            'goal_time', 
            'goal_type', 
            'description',  # FIXED: new field (was 'notes')
            'status'        # FIXED: new field added
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
            'start_time': forms.TimeInput(attrs={  # FIXED: was 'time'
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
            'goal_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={  # NEW FIELD
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Race strategy, goals, or special notes...',
            }),
            'status': forms.Select(attrs={  # NEW FIELD
                'class': 'form-control',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful labels
        self.fields['title'].label = "Race Name"
        self.fields['sport'].label = "Sport Type"
        self.fields['start_time'].label = "Start Time"
        self.fields['goal_type'].label = "Goal Type"
        self.fields['description'].label = "Race Description"
        self.fields['status'].label = "Status"