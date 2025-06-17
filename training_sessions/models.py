"""
Training session models.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from training_calendar.constants import SPORT_CHOICES, STATUS_CHOICES, INTENSITY_CHOICES
from django.core.validators import MinValueValidator, MaxValueValidator


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


class TrainingRepetition(models.Model):
    """
    Simple repetitions/intervals within a training session.
    """
    DISTANCE_UNITS = [
        ('m', 'Meters'),
        ('km', 'Kilometers'),
    ]
    
    TIME_UNITS = [
        ('sec', 'Seconds'),
        ('min', 'Minutes'),
    ]
    
    session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        related_name='repetitions'
    )
    
    # Block grouping
    block_number = models.PositiveIntegerField(
        default=1,
        help_text="Which block this repetition belongs to"
    )
    
    block_repeat_count = models.PositiveIntegerField(
        default=1,
        help_text="How many times to repeat this entire block"
    )
    
    repetition_number = models.PositiveIntegerField(
        help_text="Order of this repetition within the block (1, 2, 3...)"
    )
    
    repetition_count = models.PositiveIntegerField(
        default=1,
        help_text="How many times to repeat this individual repetition"
    )

    # Training target - distance OR time
    distance = models.FloatField(
        blank=True,
        null=True,
        help_text="Distance for this repetition"
    )
    
    distance_unit = models.CharField(
        max_length=3,
        choices=DISTANCE_UNITS,
        default='m',
        blank=True
    )
    
    duration_value = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Duration value (number)"
    )
    
    duration_unit = models.CharField(
        max_length=3,
        choices=TIME_UNITS,
        default='min',
        blank=True
    )
    
    # Intensity - both percentage and descriptive
    intensity_percentage = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Intensity as percentage of maximum (e.g., 85 for 85%)",
        validators=[MinValueValidator(1), MaxValueValidator(200)]
    )
    
    intensity = models.CharField(
        max_length=20,
        choices=INTENSITY_CHOICES,
        blank=True,
        help_text="General intensity level"
    )
    
    # Rest - time OR distance
    rest_time_value = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Rest time value (number)"
    )
    
    rest_time_unit = models.CharField(
        max_length=3,
        choices=TIME_UNITS,
        default='min',
        blank=True
    )
    
    rest_distance_value = models.FloatField(
        blank=True,
        null=True,
        help_text="Rest distance value"
    )
    
    rest_distance_unit = models.CharField(
        max_length=3,
        choices=DISTANCE_UNITS,
        default='m',
        blank=True
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Specific notes for this repetition"
    )

    block_rest_time_value = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Rest time after completing the entire block"
    )
    
    block_rest_time_unit = models.CharField(
        max_length=3,
        choices=TIME_UNITS,
        default='min',
        blank=True,
        help_text="Unit for block rest time"
    )
    
    class Meta:
        app_label = 'training_sessions'
        ordering = ['block_number', 'repetition_number']
        unique_together = ['session', 'block_number', 'repetition_number']
    
    def __str__(self):
        return f"Block {self.block_number}, Rep {self.repetition_number} - {self.session.title}"
    
    @property
    def target_formatted(self):
        """Return the main training target (distance or time)"""
        if self.distance:
            return f"{self.distance}{self.distance_unit}"
        elif self.duration_value:
            return f"{self.duration_value}{self.duration_unit}"
        return "Not specified"
    
    @property
    def intensity_formatted(self):
        """Return formatted intensity"""
        parts = []
        if self.intensity_percentage:
            parts.append(f"{self.intensity_percentage}%")
        if self.intensity:
            parts.append(self.get_intensity_display())
        return " / ".join(parts) if parts else "Not specified"
    
    @property
    def rest_formatted(self):
        """Return formatted rest time/distance"""
        if self.rest_time_value:
            return f"{self.rest_time_value}{self.rest_time_unit}"
        elif self.rest_distance_value:
            return f"{self.rest_distance_value}{self.rest_distance_unit}"
        return "No rest"
    
    @property
    def block_formatted(self):
        """Return formatted block info"""
        if self.block_repeat_count > 1:
            return f"Block {self.block_number} (×{self.block_repeat_count})"
        return f"Block {self.block_number}"
    
    @property
    def repetition_formatted(self):
        """Return formatted repetition info"""
        if self.repetition_count > 1:
            return f"Rep {self.repetition_number} (×{self.repetition_count})"
        return f"Rep {self.repetition_number}"