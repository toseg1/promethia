"""
Training session models.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TrainingSession(models.Model):
    """
    Training sessions for athletes.
    """
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    SPORT_CHOICES = [
        ('running', 'Running'),
        ('swimming', 'Swimming'),
        ('cycling', 'Cycling'),
        ('trail', 'Trail Running'),
        ('triathlon', 'Triathlon'),
        ('duathlon', 'Duathlon'),
        ('other', 'Other'),
    ]

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
    description = models.TextField(blank=True)

    # Scheduling
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=60, blank=True, null=True)

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planned')

    # Notes
    notes = models.TextField(blank=True)

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
        ordering = ['date', 'time']

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