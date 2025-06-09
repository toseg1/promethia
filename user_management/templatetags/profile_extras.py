from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def profile_image_or_initials(user):
    """Return profile image URL or generate initials badge"""
    if user.profile.profile_picture:
        return f'<img src="{user.profile.profile_picture.url}" class="img-circle elevation-2" alt="User Image" style="width: 33px; height: 33px;">'
    else:
        # Generate initials
        first_initial = user.first_name[0].upper() if user.first_name else 'U'
        last_initial = user.last_name[0].upper() if user.last_name else 'U'
        initials = f"{first_initial}{last_initial}"
        
        # Generate colored background based on user ID
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        color = colors[user.id % len(colors)]
        
        return f'''<div class="img-circle elevation-2 d-flex align-items-center justify-content-center" 
                        style="width: 33px; height: 33px; background-color: {color}; color: white; font-weight: bold; font-size: 14px;">
                     {initials}
                   </div>'''

@register.filter  
def profile_image_or_initials_large(user):
    """Larger version for profile pages"""
    if user.profile.profile_picture:
        return f'<img src="{user.profile.profile_picture.url}" class="img-circle elevation-2" alt="User Image" style="width: 128px; height: 128px;">'
    else:
        first_initial = user.first_name[0].upper() if user.first_name else 'U'
        last_initial = user.last_name[0].upper() if user.last_name else 'U'
        initials = f"{first_initial}{last_initial}"
        
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        color = colors[user.id % len(colors)]
        
        return f'''<div class="img-circle elevation-2 d-flex align-items-center justify-content-center" 
                        style="width: 128px; height: 128px; background-color: {color}; color: white; font-weight: bold; font-size: 36px;">
                     {initials}
                   </div>'''