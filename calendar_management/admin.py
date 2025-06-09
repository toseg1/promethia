# calendar_management/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CustomEvent


@admin.register(CustomEvent)
class CustomEventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'user_link', 
        'colored_preview', 
        'date_range', 
        'duration_display',
        'created_at'
    ]
    list_filter = [
        'color',
        'start_date',
        'end_date',
        'created_at',
        'user__is_staff'
    ]
    search_fields = [
        'title',
        'note',
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email'
    ]
    raw_id_fields = ['user']
    readonly_fields = [
        'created_at', 
        'updated_at',
        'duration_days_display',
        'preview_card'
    ]
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'note', 'user')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'duration_days_display')
        }),
        ('Appearance', {
            'fields': ('color', 'preview_card')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Display user with link to change page"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.user.get_full_name() or obj.user.username
            )
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__last_name'
    
    def colored_preview(self, obj):
        """Display color preview"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; '
            'border: 1px solid #ccc; border-radius: 3px; display: inline-block;"></div>',
            obj.color
        )
    colored_preview.short_description = 'Color'
    
    def date_range(self, obj):
        """Display date range"""
        if obj.start_date == obj.end_date:
            return obj.start_date.strftime('%Y-%m-%d')
        return f"{obj.start_date.strftime('%Y-%m-%d')} → {obj.end_date.strftime('%Y-%m-%d')}"
    date_range.short_description = 'Date Range'
    date_range.admin_order_field = 'start_date'
    
    def duration_display(self, obj):
        """Display duration in days"""
        days = obj.duration_days
        if days == 1:
            return "1 day"
        return f"{days} days"
    duration_display.short_description = 'Duration'
    
    def duration_days_display(self, obj):
        """Readonly field showing duration"""
        if obj.pk:
            days = obj.duration_days
            if days == 1:
                return "Single day event"
            return f"Multi-day event ({days} days)"
        return "Will be calculated after saving"
    duration_days_display.short_description = 'Event Duration'
    
    def preview_card(self, obj):
        """Display a preview of how the event card will look"""
        if obj.pk:
            preview_html = f"""
            <div style="
                background-color: {obj.color}20; 
                border-left: 3px solid {obj.color}; 
                border-radius: 4px; 
                padding: 8px 12px; 
                margin: 8px 0;
                max-width: 300px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            ">
                <div style="display: flex; align-items: flex-start; gap: 6px;">
                    <div style="color: {obj.color}; margin-top: 2px;">
                        ⭐
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #495057; font-size: 13px;">
                            {obj.title}
                        </div>
                        <div style="font-size: 11px; color: #6c757d; margin-top: 2px;">
                            {obj.date_range}
                        </div>
                        {f'<div style="font-size: 11px; color: #6c757d; margin-top: 2px; line-height: 1.2;">{obj.note[:50]}{"..." if len(obj.note) > 50 else ""}</div>' if obj.note else ''}
                    </div>
                </div>
            </div>
            """
            return mark_safe(preview_html)
        return "Save the event to see preview"
    preview_card.short_description = 'Card Preview'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('user')
    
    def save_model(self, request, obj, form, change):
        """Custom save logic"""
        if not change:  # Creating new object
            # If no user specified and not superuser, assign current user
            if not obj.user and not request.user.is_superuser:
                obj.user = request.user
        
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        """Permission logic for changing events"""
        if request.user.is_superuser:
            return True
        
        if obj is not None:
            # Users can only edit their own events
            return obj.user == request.user
        
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Permission logic for deleting events"""
        if request.user.is_superuser:
            return True
        
        if obj is not None:
            # Users can only delete their own events
            return obj.user == request.user
        
        return True
    
    def get_readonly_fields(self, request, obj=None):
        """Dynamic readonly fields based on user permissions"""
        readonly_fields = list(self.readonly_fields)
        
        # Non-superusers cannot change the user field on existing objects
        if not request.user.is_superuser and obj is not None:
            readonly_fields.append('user')
        
        return readonly_fields
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize foreign key fields"""
        if db_field.name == "user" and not request.user.is_superuser:
            # Non-superusers can only select themselves
            kwargs["queryset"] = request.user.__class__.objects.filter(pk=request.user.pk)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    actions = ['duplicate_events', 'export_events']
    
    def duplicate_events(self, request, queryset):
        """Duplicate selected events"""
        from datetime import timedelta
        
        duplicated_count = 0
        for event in queryset:
            # Create a copy with dates moved forward by 7 days
            new_event = CustomEvent(
                user=event.user,
                title=f"{event.title} (Copy)",
                note=event.note,
                color=event.color,
                start_date=event.start_date + timedelta(days=7),
                end_date=event.end_date + timedelta(days=7)
            )
            new_event.save()
            duplicated_count += 1
        
        self.message_user(
            request,
            f"Successfully duplicated {duplicated_count} event(s) with dates moved forward by 7 days."
        )
    duplicate_events.short_description = "Duplicate selected events (7 days later)"
    
    def export_events(self, request, queryset):
        """Export selected events to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="custom_events.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Title', 'User', 'Start Date', 'End Date', 
            'Duration (days)', 'Color', 'Note', 'Created'
        ])
        
        for event in queryset:
            writer.writerow([
                event.title,
                event.user.get_full_name() if event.user else '',
                event.start_date,
                event.end_date,
                event.duration_days,
                event.color,
                event.note,
                event.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_events.short_description = "Export selected events to CSV"


# Custom admin site configuration
admin.site.site_header = "Euphron Training Administration"
admin.site.site_title = "Euphron Admin"
admin.site.index_title = "Welcome to Euphron Training Administration"