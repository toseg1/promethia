"""
URL configuration for user management app.
"""
from django.urls import path, include
from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('athletes/add/', views.add_athlete, name='add_athlete'),
    path('accept-coach/<int:relationship_id>/', views.accept_coach, name='accept_coach'),
    path('decline-coach/<int:relationship_id>/', views.decline_coach, name='decline_coach'),
    path('switch-view/', views.switch_view, name='switch_view'),
    path('athlete-detail/<int:athlete_id>/', views.athlete_detail, name='athlete_detail'),
    path('remove-athlete/<int:athlete_id>/', views.remove_athlete, name='remove_athlete'),
    path('vma-calculator/', views.vma_calculator, name='vma_calculator'),
    path('calendar/', include('calendar_management.urls')), 
    path('profile/remove-picture/', views.remove_profile_picture, name='remove_profile_picture'),

]