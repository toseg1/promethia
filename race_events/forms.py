"""
Forms for race_events app.
"""
from django import forms
from .models import Race


class RaceForm(forms.ModelForm):
    """Form for creating and editing races."""
    
    class Meta:
        model = Race
        fields = ['name', 'sport_type', 'date', 'time', 'location', 'venue', 
                 'distance', 'goal_time', 'goal_type', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Paris Marathon 2025',
                'id': 'raceName'
            }),
            'sport_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'sportType'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'raceDate'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'raceTime'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Paris, France',
                'id': 'raceLocation'
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., City Marathon Association',
                'id': 'raceVenue'
            }),
            'distance': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 42.2km, Sprint, Half',
                'id': 'raceDistance'
            }),
            'goal_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'goalType'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Training plan, special requirements, motivation, etc...',
                'id': 'raceNotes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
