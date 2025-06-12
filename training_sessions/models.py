"""
Training session models.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from training_calendar.constants import SPORT_CHOICES, STATUS_CHOICES, INTENSITY_CHOICES

class TrainingSession(models.Model):
    """
    Training sessions for athletes.
    """
    # Basic information
    athlete = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='training_sessions',
        limit_choices_to={'profile__role': 'athlete'}
    )
    
    sport = models.CharField(
        max_length=20,
        choices=SPORT_CHOICES,
        default='running'
    )
    
    title = models.CharField(max_length=200)

    # ADD description field (around line 45)  
    description = models.TextField(
        blank=True,
        help_text="Detailed workout description, instructions, or plan"
    )

    # Scheduling
    date = models.DateField()

    start_time = models.TimeField(
        blank=True, 
        null=True,
        help_text="Planned start time"
    )
    
    distance = models.FloatField(
        blank=True,
        null=True,
        help_text="Planned distance in km"
    )

    intensity = models.CharField(
        max_length=20,
        choices=INTENSITY_CHOICES,
        blank=True,
        default='moderate'
    )

    duration_minutes = models.PositiveIntegerField(default=60, blank=True, null=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    # Who created it
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_sessions'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'training_sessions'
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} - {self.athlete.get_full_name()} ({self.date})"
    
    @property
    def duration_formatted(self):
        """Return duration in h:m:s format"""
        if not self.duration_minutes:
            return "0:00:00"
        
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        seconds = 0  # Since we only store minutes
        
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    @property
    def is_past(self):
        """Check if session date is in the past."""
        session_datetime = timezone.datetime.combine(self.date, self.time)
        return timezone.make_aware(session_datetime) < timezone.now()

    def mark_completed(self):
        """Mark session as completed."""
        self.status = 'completed'
        self.save()

    @property
    def sport_color(self):
        """Get color for this sport from constants."""
        from training_calendar.constants import SPORT_COLORS
        return SPORT_COLORS.get(self.sport, '#6c757d')

    @property
    def sport_icon(self):
        """Get icon for this sport from constants."""
        from training_calendar.constants import SPORT_ICONS
        return SPORT_ICONS.get(self.sport, 'fas fa-dumbbell')