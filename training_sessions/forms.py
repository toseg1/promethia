"""
Forms for training sessions.
"""
from django import forms
from django.contrib.auth.models import User
from .models import TrainingSession
from user_management.models import CoachAthleteRelationship

# Define sport choices locally to avoid circular import
SPORT_CHOICES = [
    ('running', 'Running'),
    ('swimming', 'Swimming'),
    ('cycling', 'Cycling'),
    ('trail', 'Trail Running'),
    ('triathlon', 'Triathlon'),
    ('duathlon', 'Duathlon'),
    ('other', 'Other'),
]

class TrainingSessionForm(forms.ModelForm):
    """Form for creating and editing training sessions."""
    sport = forms.ChoiceField(
        choices=SPORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, athlete_choices=None, user=None, current_view=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if athlete_choices:
            # Convert to proper choice format and set as ModelChoiceField
            athlete_ids = [choice[0] for choice in athlete_choices]
            
            # If coach is in athlete view, add themselves to the choices
            if (user and current_view == 'athlete' and 
                user.profile.role == 'coach' and 
                user.id not in athlete_ids):
                athlete_ids.append(user.id)
            
            self.fields['athlete'] = forms.ModelChoiceField(
                queryset=User.objects.filter(id__in=athlete_ids),
                empty_label=None,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        elif user:
            # Handle cases where no athlete_choices are provided
            if current_view == 'athlete':
                if user.profile.role == 'coach':
                    # Coach in athlete view - only show themselves
                    self.fields['athlete'] = forms.ModelChoiceField(
                        queryset=User.objects.filter(id=user.id),
                        initial=user,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
                else:
                    # Regular athlete - only show themselves
                    self.fields['athlete'] = forms.ModelChoiceField(
                        queryset=User.objects.filter(id=user.id),
                        initial=user,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
            elif current_view == 'coach' and user.profile.role == 'coach':
                # Coach in coach view - show their coached athletes
                coached_relationships = CoachAthleteRelationship.objects.filter(
                    coach=user,
                    status='active'
                )
                athlete_ids = [rel.athlete.id for rel in coached_relationships]
                self.fields['athlete'].queryset = User.objects.filter(
                    id__in=athlete_ids,
                    profile__role='athlete'
                )
        
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            if field_name not in ['athlete', 'sport']:  # these fields already have class
                field.widget.attrs['class'] = 'form-control'
        
        # Specific widget customizations
        self.fields['date'].widget = forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )
        self.fields['time'].widget = forms.TimeInput(
            attrs={'class': 'form-control', 'type': 'time'}
        )
        self.fields['description'].widget = forms.Textarea(
            attrs={'class': 'form-control', 'rows': 3}
        )
        self.fields['notes'].widget = forms.Textarea(
            attrs={'class': 'form-control', 'rows': 3}
        )

    class Meta:
        model = TrainingSession
        fields = ['athlete', 'sport', 'title', 'description', 'date', 'time', 'duration_minutes', 'status', 'notes']

    def save(self, commit=True):
        session = super().save(commit=False)
        
        # Ensure athlete is properly set
        if 'athlete' in self.cleaned_data:
            athlete = self.cleaned_data['athlete']
            if isinstance(athlete, User):
                session.athlete = athlete
            elif isinstance(athlete, str) and athlete.isdigit():
                try:
                    session.athlete = User.objects.get(id=int(athlete))
                except User.DoesNotExist:
                    raise forms.ValidationError("Selected athlete does not exist.")
            else:
                raise forms.ValidationError("Invalid athlete selection.")
        
        if commit:
            session.save()
        return session