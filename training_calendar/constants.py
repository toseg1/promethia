"""
Shared constants for the training calendar application.
This file ensures consistency across all apps.
"""

# Sport choices - standardized across all models
SPORT_CHOICES = [
    ('running', 'Running'),
    ('swimming', 'Swimming'),
    ('cycling', 'Cycling'),
    ('trail', 'Trail Running'),
    ('triathlon', 'Triathlon'),
    ('duathlon', 'Duathlon'),
    ('other', 'Other'),
]

# Status choices for events (training sessions and races)
STATUS_CHOICES = [
    ('planned', 'Planned'),
    ('scheduled', 'Scheduled'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('missed', 'Missed'),
]

# Goal types for races
RACE_GOAL_CHOICES = [
    ('finish', 'Just Finish'),
    ('pb', 'Personal Best'),
    ('time', 'Specific Time'),
    ('placement', 'Top Placement'),
    ('qualify', 'Qualify for Event'),
    ('experience', 'Experience/Fun'),
]

# Intensity levels for training
INTENSITY_CHOICES = [
    ('recovery', 'Recovery'),
    ('easy', 'Easy'),
    ('moderate', 'Moderate'),
    ('hard', 'Hard'),
    ('very_hard', 'Very Hard'),
]

# Sport colors for UI consistency
SPORT_COLORS = {
    'running': '#28a745',      # Green
    'swimming': '#17a2b8',     # Teal  
    'cycling': '#007bff',      # Blue
    'trail': '#6f42c1',        # Purple
    'triathlon': '#fd7e14',    # Orange
    'other': '#6c757d',        # Gray
}

# Sport icons for UI consistency  
SPORT_ICONS = {
    'running': 'fas fa-running',
    'swimming': 'fas fa-swimmer', 
    'cycling': 'fas fa-bicycle',
    'trail': 'fas fa-mountain',
    'triathlon': 'fas fa-fire',
    'other': 'fas fa-dumbbell',
}

# Common field names - for reference during standardization
FIELD_NAMES = {
    'sport': 'sport',           # Standardize on 'sport' for all models
    'title': 'title',           # Standardize on 'title' for all models
    'description': 'description', # Standardize on 'description' for all models
    'start_time': 'start_time',  # Standardize on 'start_time' for all models
    'status': 'status',         # Standardize on 'status' for all models
}