"""
URL configuration for races app.
"""
from django.urls import path
from . import views

app_name = 'race_events'

urlpatterns = [
    path('', views.race_list, name='race_list'),
    path('add/', views.race_create, name='race_create'),
    path('race/<int:race_id>/', views.race_detail, name='race_detail'),
    path('race/<int:race_id>/edit/', views.race_edit, name='race_edit'),
    path('race/<int:race_id>/delete/', views.race_delete, name='race_delete'),
    path('race/<int:race_id>/result/', views.race_result, name='race_result'),
    path('coach/', views.coach_race_list_view, name='coach_race_list'),
    path('athlete/', views.athlete_race_list_view, name='athlete_race_list'),
    
]