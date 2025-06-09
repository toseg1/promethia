# calendar_management/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class CustomEvent(models.Model):
    """Model for custom events that users can create on their calendar"""
    
    COLOR_CHOICES = [
        ('#007bff', 'Blue'),
        ('#28a745', 'Green'),
        ('#ffc107', 'Yellow'),
        ('#dc3545', 'Red'),
        ('#6c757d', 'Gray'),
        ('#17a2b8', 'Teal'),
        ('#6f42c1', 'Purple'),
        ('#fd7e14', 'Orange'),
        ('#e83e8c', 'Pink'),
        ('#20c997', 'Mint'),
    ]
    
    color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message='Enter a valid hex color code (e.g., #007bff)'
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='custom_events'
    )
    title = models.CharField(
        max_length=200,
        help_text="Title of your custom event"
    )
    note = models.TextField(
        blank=True,
        help_text="Additional notes about this event"
    )
    color = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        default='#007bff',
        validators=[color_validator],
        help_text="Color to display this event on the calendar"
    )
    start_date = models.DateField(
        help_text="Start date of the event"
    )
    end_date = models.DateField(
        help_text="End date of the event"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date', 'title']
        verbose_name = 'Custom Event'
        verbose_name_plural = 'Custom Events'
    
    def __str__(self):
        if self.start_date == self.end_date:
            return f"{self.title} ({self.start_date})"
        return f"{self.title} ({self.start_date} - {self.end_date})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Only validate if both dates exist
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError('End date cannot be before start date.')
    
    @property
    def is_multi_day(self):
        """Check if the event spans multiple days"""
        return self.start_date != self.end_date
    
    @property
    def duration_days(self):
        """Get the number of days this event spans"""
        return (self.end_date - self.start_date).days + 1