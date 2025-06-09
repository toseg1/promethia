

from django.urls import path
from . import views

app_name = 'calendar_management'

urlpatterns = [
    path('', views.calendar_view, name='view'),
    path('create-custom/', views.create_custom_event, name='create_custom_event'),
    path('custom/<int:event_id>/', views.custom_event_detail, name='custom_event_detail'), 
    # Custom event creation
    path('custom-event/create/', views.create_custom_event, name='create_custom_event'),
    # Custom event editing (reuses the same view)
    path('custom-event/edit/<int:event_id>/', views.create_custom_event, name='edit_custom_event'),
    # Custom event deletion
    path('custom-event/delete/<int:event_id>/', views.delete_custom_event, name='delete_custom_event'),
    path('coach/', views.CoachCalendarView.as_view(), name='coach_view'),
    path('coach/athlete/<int:athlete_id>/', views.CoachAthleteCalendarView.as_view(), name='coach_athlete_view'),
]