"""
User management models for profiles and relationships.
"""
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Extended user profile for coaches and athletes.
    """
    ROLE_CHOICES = [
        ('coach', 'Coach'),
        ('athlete', 'Athlete'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='athlete')
    
    # Basic information
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    
    date_of_birth = models.DateField(blank=True, null=True, help_text="Used to calculate age automatically")
    club = models.CharField(max_length=100, blank=True, help_text="Sports club or team")
    
    # Sport metrics
    vma = models.FloatField(blank=True, null=True, help_text="Maximal Aerobic Speed (km/h)")
    vma_updated = models.DateField(blank=True, null=True)
    ftp = models.IntegerField(blank=True, null=True, help_text="Functional Threshold Power (watts)")
    ftp_updated = models.DateField(blank=True, null=True)
    css = models.CharField(max_length=10, blank=True, help_text="Critical Swim Speed (e.g., 1:30/100m)")
    css_updated = models.DateField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'user_management'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

    @property
    def is_coach(self):
        return self.role == 'coach'

    @property
    def is_athlete(self):
        return self.role == 'athlete'
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
class CoachAthleteRelationship(models.Model):
    """
    Relationship between coaches and athletes.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('ended', 'Ended'),
    ]

    coach = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='coached_athletes',
        limit_choices_to={'profile__role': 'coach'}
    )
    athlete = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='coaches',
        limit_choices_to={'profile__role': 'athlete'}
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'user_management'
        unique_together = ['coach', 'athlete']

    def __str__(self):
        return f"{self.coach.get_full_name()} coaches {self.athlete.get_full_name()}"

    def accept(self):
        """Accept the coaching relationship."""
        self.status = 'active'
        self.save()

    def end(self):
        """End the coaching relationship."""
        self.status = 'ended'
        self.save()


# Signal to automatically create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()