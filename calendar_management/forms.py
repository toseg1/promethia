# calendar_management/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomEvent


class CustomEventForm(forms.ModelForm):
    """Form for creating and editing custom events"""
    
    class Meta:
        model = CustomEvent
        fields = ['title', 'note', 'color', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title...',
                'maxlength': 200,
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add any additional notes...',
            }),
            'color': forms.Select(attrs={
                'class': 'form-control color-picker',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        labels = {
            'title': 'Event Title',
            'note': 'Notes',
            'color': 'Calendar Color',
            'start_date': 'Start Date',
            'end_date': 'End Date',
        }
        help_texts = {
            'title': 'Give your event a descriptive title',
            'note': 'Add any relevant details about this event',
            'color': 'Choose a color to help identify this event type',
            'start_date': 'When does this event start?',
            'end_date': 'When does this event end? (can be same day)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError('End date cannot be before start date.')
            
            # Optional: Add validation for maximum duration
            duration = (end_date - start_date).days
            if duration > 365:  # Maximum 1 year
                raise ValidationError('Event duration cannot exceed one year.')
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields explicitly
        self.fields['title'].required = True
        self.fields['start_date'].required = True  
        self.fields['end_date'].required = True
        
        # Optional fields
        self.fields['note'].required = False
        self.fields['color'].required = False
        
        # Add CSS classes for better styling
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['data-field'] = field_name
        