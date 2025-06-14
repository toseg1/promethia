"""
Logging utilities for Promethia training calendar.
"""
import logging
from typing import Optional, Any

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the promethia prefix."""
    return logging.getLogger(f'promethia.{name}')

def get_username(user: Any) -> str:
    """Safely get username from user object."""
    if hasattr(user, 'username'):
        return user.username
    elif hasattr(user, 'is_authenticated') and not user.is_authenticated:
        return 'anonymous'
    else:
        return 'unknown'

def log_error(logger: logging.Logger, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
    """Log an error with optional exception details."""
    if exception:
        logger.error(f"{message}: {str(exception)}", exc_info=True, extra=kwargs)
    else:
        logger.error(message, extra=kwargs)

def log_warning(logger: logging.Logger, message: str, **kwargs) -> None:
    """Log a warning message."""
    logger.warning(message, extra=kwargs)

def log_info(logger: logging.Logger, message: str, **kwargs) -> None:
    """Log an info message."""
    logger.info(message, extra=kwargs)

def log_debug(logger: logging.Logger, message: str, **kwargs) -> None:
    """Log a debug message."""
    logger.debug(message, extra=kwargs)

def log_user_action(logger: logging.Logger, user: Any, action: str, details: str = '') -> None:
    """Log user actions for audit trail."""
    username = get_username(user)
    logger.info(f"User {username} {action}", extra={
        'user': username,
        'action': action,
        'details': details
    })

# Common error messages
class ErrorMessages:
    """Centralized error messages for consistency."""
    
    # Model errors
    MODEL_NOT_FOUND = "Model not available: {model_name}"
    IMPORT_ERROR = "Failed to import module: {module_name}"
    FIELD_ACCESS_ERROR = "Error accessing field '{field}' on model '{model}'"
    
    # Form errors
    FORM_VALIDATION_ERROR = "Form validation failed: {form_name}"
    FORM_SAVE_ERROR = "Error saving form: {form_name}"
    
    # View errors
    PERMISSION_DENIED = "Permission denied for user {user} on {action}"
    UNEXPECTED_ERROR = "Unexpected error in {location}: {error}"
    
    # Database errors
    DATABASE_ERROR = "Database error: {error}"
    MIGRATION_ERROR = "Migration error: {error}"
    
    # User messages (friendly)
    USER_FORM_ERROR = "Please correct the errors below and try again."
    USER_PERMISSION_ERROR = "You don't have permission to perform this action."
    USER_UNEXPECTED_ERROR = "An unexpected error occurred. Please try again or contact support."