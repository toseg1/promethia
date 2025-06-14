"""
User-friendly message handling for Promethia.
"""
from django.contrib import messages
from django.http import HttpRequest
from typing import Optional
import logging

logger = logging.getLogger('promethia.messages')

def get_safe_username(user) -> str:
    """Safely get username from user object."""
    if hasattr(user, 'username'):
        return user.username
    elif hasattr(user, 'is_authenticated') and not user.is_authenticated:
        return 'anonymous'
    else:
        return 'unknown'

class UserMessages:
    """Centralized user message handling."""
    
    @staticmethod
    def success(request: HttpRequest, message: str, log_message: Optional[str] = None) -> None:
        """Show success message to user and optionally log."""
        messages.success(request, message)
        if log_message:
            username = get_safe_username(request.user)
            logger.info(log_message, extra={'user': username})
    
    @staticmethod
    def error(request: HttpRequest, message: str, log_message: Optional[str] = None, exception: Optional[Exception] = None) -> None:
        """Show error message to user and log the technical details."""
        messages.error(request, message)
        if log_message:
            username = get_safe_username(request.user)
            if exception:
                logger.error(f"{log_message}: {str(exception)}", exc_info=True, 
                           extra={'user': username})
            else:
                logger.error(log_message, extra={'user': username})
    
    @staticmethod
    def warning(request: HttpRequest, message: str, log_message: Optional[str] = None) -> None:
        """Show warning message to user and optionally log."""
        messages.warning(request, message)
        if log_message:
            username = get_safe_username(request.user)
            logger.warning(log_message, extra={'user': username})
    
    @staticmethod
    def info(request: HttpRequest, message: str, log_message: Optional[str] = None) -> None:
        """Show info message to user and optionally log."""
        messages.info(request, message)
        if log_message:
            username = get_safe_username(request.user)
            logger.info(log_message, extra={'user': username})
    
    # Common user messages
    MESSAGES = {
        # Success messages
        'race_created': 'Race "{title}" created successfully!',
        'race_updated': 'Race "{title}" updated successfully!',
        'race_deleted': 'Race "{title}" deleted successfully!',
        'session_created': 'Training session "{title}" created successfully!',
        'session_updated': 'Training session "{title}" updated successfully!',
        'session_deleted': 'Training session "{title}" deleted successfully!',
        'profile_updated': 'Your profile has been updated successfully!',
        
        # Error messages
        'permission_denied': 'You do not have permission to perform this action.',
        'form_error': 'Please correct the errors below and try again.',
        'unexpected_error': 'An unexpected error occurred. Please try again.',
        'save_error': 'Unable to save your changes. Please try again.',
        'delete_error': 'Unable to delete this item. Please try again.',
        
        # Warning messages
        'incomplete_profile': 'Please complete your profile to get the most out of Promethia.',
        'no_data': 'No data available for the selected period.',
        
        # Info messages
        'first_login': 'Welcome to Promethia! Start by creating your first training session or race.',
        'maintenance': 'Some features may be temporarily unavailable due to maintenance.',
    }

