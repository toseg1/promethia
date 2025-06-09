"""
Context processors for making variables available in all templates.
"""

def view_context_processor(request):
    """Add current view mode to all template contexts."""
    if request.user.is_authenticated:
        # Check session first
        session_view = request.session.get('view_mode')
        if session_view in ['athlete', 'coach']:
            current_view = session_view
        else:
            # Default to user's role
            current_view = request.user.profile.role
        
        return {
            'current_view': current_view
        }
    return {}