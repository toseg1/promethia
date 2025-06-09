"""
URL configuration for training sessions app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar_view'),
    path('session/create/', views.session_create, name='session_create'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('session/<int:session_id>/edit/', views.session_edit, name='session_edit'),
    path('session/<int:session_id>/delete/', views.session_delete, name='session_delete'),
    path('session/<int:session_id>/complete/', views.session_completed, name='session_completed'),
    ]