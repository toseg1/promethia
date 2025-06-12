"""
Race management models.
"""
from django.db import models
from django.contrib.auth.models import User
from training_calendar.constants import SPORT_CHOICES, STATUS_CHOICES, RACE_GOAL_CHOICES

class Race(models.Model):
    """
    Races and events for athletes.
    """
    # Basic information
    athlete = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='races',
        limit_choices_to={'profile__role': 'athlete'}
    )
    title = models.CharField(
        max_length=200, 
        help_text="e.g., Paris Marathon 2025"
    )

    sport = models.CharField(max_length=20, 
                             choices=SPORT_CHOICES, 
                             default='running')

    description = models.TextField(
        blank=True,
        help_text="Race details, strategy, or notes"
    )
    
    # When and where
    date = models.DateField()

    start_time = models.TimeField(
        blank=True, 
        null=True,
        help_text="Race start time"
    )
    
    location = models.CharField(max_length=200)

    venue = models.CharField(max_length=200, blank=True)
    
    # Race details
    distance = models.CharField(max_length=50, blank=True, help_text="e.g., 42.2km, Sprint, Half")
    
    # Goals
    goal_time = models.CharField(max_length=20, blank=True, help_text="e.g., 3:30:00")
    goal_type = models.CharField(
        max_length=20,
        choices=RACE_GOAL_CHOICES,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']
        app_label = 'race_events'

    def __str__(self):
       return f"{self.title} - {self.athlete.get_full_name()} ({self.date})"

    @property
    def is_past(self):
        """Check if race date is in the past."""
        from datetime import date
        return self.date < date.today()

    @property
    def days_until_race(self):
        """Calculate days until race."""
        from datetime import date
        delta = self.date - date.today()
        return delta.days if delta.days >= 0 else 0


class RaceResult(models.Model):
    """
    Results for completed races.
    """
    race = models.OneToOneField(Race, on_delete=models.CASCADE, related_name='result')
    
    # Performance data
    finish_time = models.CharField(max_length=20, blank=True, help_text="Actual finish time")
    overall_position = models.PositiveIntegerField(blank=True, null=True)
    category_position = models.PositiveIntegerField(blank=True, null=True)
    total_participants = models.PositiveIntegerField(blank=True, null=True)
    
    # Satisfaction
    SATISFACTION_CHOICES = [
        (1, 'Very Disappointed'),
        (2, 'Disappointed'),
        (3, 'Neutral'),
        (4, 'Satisfied'),
        (5, 'Very Satisfied'),
    ]
    satisfaction = models.IntegerField(choices=SATISFACTION_CHOICES, blank=True, null=True)
    
    # Notes
    race_report = models.TextField(blank=True, help_text="How did the race go?")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'race_events'

    def __str__(self):
        return f"Result for {self.race.name}"

    @property
    def goal_achieved(self):
        """Check if goal was achieved."""
        if self.race.goal_time and self.finish_time:
            # Simple string comparison - could be improved with proper time parsing
            return self.finish_time <= self.race.goal_time
        return None