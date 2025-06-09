/**
 * Enhanced Calendar JavaScript - UNIFIED WEEKLY/MONTHLY VIEW
 * Both views now use the same styling and interactions
 */

// Calendar utility functions
const CalendarUtils = {
    /**
     * Format time duration for display
     */
    formatDuration: function(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
    },

    /**
     * Get sport color based on sport type
     */
    getSportColor: function(sport) {
        const colors = {
            'running': '#28a745',
            'cycling': '#007bff', 
            'swimming': '#17a2b8',
            'trail_running': '#6f42c1',
            'triathlon': '#fd7e14',
            'duathlon': '#e83e8c',
            'race': '#ffc107',
            'custom': '#6c757d'
        };
        return colors[sport.toLowerCase()] || colors.custom;
    },

    /**
     * Debounce function for performance
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Get date from element
     */
    getDateFromElement: function(element) {
        return element.getAttribute('data-date') || 
               element.querySelector('.day-number')?.textContent ||
               element.textContent.trim();
    }
};

// Main Calendar class
class EnhancedCalendar {
    constructor() {
        this.selectedDate = null;
        this.selectedElement = null;
        this.currentView = 'month';
        this.isLoading = false;
        this.eventCache = new Map();
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupAnimations();
        this.initializeTooltips();
        this.setupKeyboardNavigation();
        this.validateProgressBars();
        this.initializeMultiDayEvents();
        
        // Initialize based on current view
        const urlParams = new URLSearchParams(window.location.search);
        this.currentView = urlParams.get('view') || 'month';
        
        // Apply event colors
        this.applyEventColors();
        
        console.log('Enhanced Calendar initialized for view:', this.currentView);
    }

    bindEvents() {
        // UNIFIED: Day selection for both month and week views
        this.bindDaySelection();
        
        // UNIFIED: Event card interactions for both views
        this.bindEventCardInteractions();
        
        // Sport widget interactions
        this.bindSportWidgetEvents();
        
        // Navigation events
        this.bindNavigationEvents();
        
        // Resize handler
        window.addEventListener('resize', CalendarUtils.debounce(() => {
            this.handleResize();
        }, 250));
    }

    bindDaySelection() {
        // UNIFIED: Select all calendar days (works for both month and week view)
        document.querySelectorAll('.calendar-day').forEach(day => {
            if (!day.classList.contains('calendar-day-empty')) {
                day.addEventListener('click', (e) => {
                    // Don't trigger if clicking on an event card
                    if (!e.target.closest('.event-card')) {
                        e.preventDefault();
                        e.stopPropagation();
                        this.selectDay(day);
                    }
                });
                
                day.addEventListener('dblclick', (e) => {
                    // Don't trigger if clicking on an event card
                    if (!e.target.closest('.event-card')) {
                        e.preventDefault();
                        e.stopPropagation();
                        this.quickAddEvent(day);
                    }
                });
            }
        });
    }

    selectDay(dayElement) {
        if (!dayElement || dayElement.classList.contains('calendar-day-empty')) {
            return;
        }

        // CRITICAL: Remove selection from ALL days first
        document.querySelectorAll('.calendar-day').forEach(day => {
            day.classList.remove('calendar-day-selected', 'week-day-selected');
        });
        
        // Add selection to clicked day (this will override today styling due to CSS priority)
        dayElement.classList.add('calendar-day-selected');
        
        // Store selected date and element
        this.selectedElement = dayElement;
        this.selectedDate = this.getDateFromDay(dayElement);
        
        // Add pulse animation
        dayElement.classList.add('pulse');
        setTimeout(() => {
            dayElement.classList.remove('pulse');
        }, 600);
        
        // Trigger selection event
        this.onDateSelected(this.selectedDate, dayElement);
        
        console.log('Selected day:', this.selectedDate, 'View:', this.currentView);
    }

    getDateFromDay(dayElement) {
        // Try to get date from data attribute first
        let date = dayElement.getAttribute('data-date');
        if (date) return date;
        
        // Fallback: construct date from day number and current month/year
        const dayNumber = dayElement.querySelector('.day-number')?.textContent?.trim();
        if (dayNumber) {
            const monthElement = document.querySelector('[data-current-month]');
            const yearElement = document.querySelector('[data-current-year]');
            
            if (monthElement && yearElement) {
                const month = monthElement.getAttribute('data-current-month');
                const year = yearElement.getAttribute('data-current-year');
                return `${year}-${month.padStart(2, '0')}-${dayNumber.padStart(2, '0')}`;
            }
        }
        
        return null;
    }

    bindEventCardInteractions() {
        document.querySelectorAll('.event-card').forEach(event => {
            // Hover effects
            event.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.02) translateY(-1px)';
                this.style.zIndex = '15';
            });
            
            event.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1) translateY(0)';
                this.style.zIndex = '1';
            });
            
            // CRITICAL: Handle event card clicks
            event.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                this.handleEventCardClick(event);
            });
        });
    }

    handleEventCardClick(eventCard) {
        // Get the event URL from the href attribute
        const href = eventCard.getAttribute('href');
        
        if (href && href !== '#') {
            // Navigate to the event detail page
            window.location.href = href;
        } else {
            // Fallback: show event details
            this.showEventDetails(eventCard);
        }
    }

    bindSportWidgetEvents() {
        document.querySelectorAll('.sport-widget').forEach(widget => {
            widget.addEventListener('click', (e) => {
                this.handleSportWidgetClick(widget);
            });
            
            widget.addEventListener('mouseenter', (e) => {
                this.showSportDetails(widget);
            });
            
            widget.addEventListener('mouseleave', (e) => {
                this.hideSportDetails();
            });
        });
    }

    bindNavigationEvents() {
        // View toggle buttons
        document.querySelectorAll('.view-toggle .btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.changeView(e.target.closest('.btn'));
            });
        });

        // Navigation arrows with keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName.toLowerCase() === 'input') return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.navigatePrevious();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.navigateNext();
                    break;
                case 'Escape':
                    this.clearSelection();
                    break;
                case 'Enter':
                    if (this.selectedElement) {
                        this.quickAddEvent(this.selectedElement);
                    }
                    break;
            }
        });
    }

    applyEventColors() {
        // Apply correct sport colors to all event cards
        document.querySelectorAll('.event-card').forEach(eventCard => {
            // Get sport type from data attribute or class
            const sport = this.getSportFromEventCard(eventCard);
            const eventType = this.getEventTypeFromCard(eventCard);
            
            // Remove existing sport classes
            eventCard.classList.remove(
                'sport-running', 'sport-cycling', 'sport-swimming', 
                'sport-trail_running', 'sport-triathlon', 'sport-duathlon', 
                'sport-other', 'event-race', 'event-custom'
            );
            
            // Add correct class based on event type and sport
            if (eventType === 'race') {
                eventCard.classList.add('event-race');
            } else if (eventType === 'custom') {
                eventCard.classList.add('event-custom');
            } else if (sport) {
                eventCard.classList.add(`sport-${sport}`);
            } else {
                eventCard.classList.add('sport-other');
            }
        });
    }

    getSportFromEventCard(eventCard) {
        // Try to get sport from data attribute
        let sport = eventCard.getAttribute('data-sport');
        if (sport) return sport.toLowerCase();
        
        // Try to get from existing classes
        const classList = Array.from(eventCard.classList);
        for (const className of classList) {
            if (className.startsWith('sport-')) {
                return className.replace('sport-', '');
            }
        }
        
        // Try to get from icon
        const icon = eventCard.querySelector('.event-icon i, .fas, .fa');
        if (icon) {
            const iconClass = Array.from(icon.classList).find(cls => 
                cls.includes('running') || cls.includes('cycling') || 
                cls.includes('swimming') || cls.includes('bike') ||
                cls.includes('mountain') || cls.includes('medal')
            );
            
            if (iconClass) {
                if (iconClass.includes('running')) return 'running';
                if (iconClass.includes('cycling') || iconClass.includes('bike')) return 'cycling';
                if (iconClass.includes('swimming')) return 'swimming';
                if (iconClass.includes('mountain')) return 'trail_running';
                if (iconClass.includes('medal')) return 'triathlon';
            }
        }
        
        return 'other';
    }

    getEventTypeFromCard(eventCard) {
        // Check data attribute
        const eventType = eventCard.getAttribute('data-event-type');
        if (eventType) return eventType.toLowerCase();
        
        // Check for race indicators
        if (eventCard.querySelector('.fa-trophy') || 
            eventCard.textContent.toLowerCase().includes('race') ||
            eventCard.textContent.toLowerCase().includes('marathon') ||
            eventCard.textContent.toLowerCase().includes('triathlon')) {
            return 'race';
        }
        
        // Check for custom event indicators
        if (eventCard.querySelector('.fa-star') ||
            eventCard.classList.contains('custom-card')) {
            return 'custom';
        }
        
        return 'training_session';
    }

    initializeMultiDayEvents() {
        // Find events that should span multiple days
        const multiDayEvents = document.querySelectorAll('[data-event-duration]');
        
        multiDayEvents.forEach(event => {
            const duration = parseInt(event.getAttribute('data-event-duration'));
            const startDate = event.getAttribute('data-start-date');
            
            if (duration > 1 && startDate) {
                this.createMultiDayEventCards(event, startDate, duration);
            }
        });
    }

    createMultiDayEventCards(originalEvent, startDate, durationDays) {
        const eventData = {
            title: originalEvent.querySelector('.event-title')?.textContent || 'Multi-day Event',
            sport: this.getSportFromEventCard(originalEvent),
            eventType: this.getEventTypeFromCard(originalEvent)
        };
        
        // Create event cards for each day
        for (let i = 0; i < durationDays; i++) {
            const currentDate = this.addDaysToDate(startDate, i);
            const dayContainer = document.querySelector(`[data-date="${currentDate}"] .day-events`);
            
            if (dayContainer) {
                const eventCard = this.createEventCard(eventData, i === 0, i === durationDays - 1, i > 0 && i < durationDays - 1);
                dayContainer.appendChild(eventCard);
            }
        }
        
        // Remove original event if it was a placeholder
        if (originalEvent.classList.contains('multi-day-template')) {
            originalEvent.remove();
        }
    }

    createEventCard(eventData, isFirstDay, isLastDay, isMiddleDay) {
        const eventCard = document.createElement('div');
        eventCard.className = 'event-card multi-day';
        
        if (isFirstDay) eventCard.classList.add('first-day');
        if (isLastDay) eventCard.classList.add('last-day');
        if (isMiddleDay) eventCard.classList.add('middle-day');
        
        // Add sport/event type class
        if (eventData.eventType === 'race') {
            eventCard.classList.add('event-race');
        } else if (eventData.eventType === 'custom') {
            eventCard.classList.add('event-custom');
        } else {
            eventCard.classList.add(`sport-${eventData.sport}`);
        }
        
        eventCard.innerHTML = `
            <div class="event-icon">
                <i class="fas fa-${this.getIconForSport(eventData.sport)}"></i>
            </div>
            <div class="event-content">
                <div class="event-title">${eventData.title}</div>
                ${isFirstDay ? '<div class="event-time">Multi-day event</div>' : 
                  isLastDay ? '<div class="event-time">Final day</div>' : 
                  '<div class="event-time">Continues...</div>'}
            </div>
        `;
        
        return eventCard;
    }

    getIconForSport(sport) {
        const icons = {
            'running': 'running',
            'cycling': 'bicycle',
            'swimming': 'swimmer',
            'trail_running': 'mountain',
            'triathlon': 'medal',
            'duathlon': 'running',
            'race': 'trophy',
            'custom': 'star'
        };
        return icons[sport] || 'heartbeat';
    }

    addDaysToDate(dateString, days) {
        const date = new Date(dateString);
        date.setDate(date.getDate() + days);
        return date.toISOString().split('T')[0];
    }

    quickAddEvent(element) {
        if (!element) return;
        
        const date = this.getDateFromDay(element);
        
        if (date) {
            this.showQuickAddModal(date);
        }
        
        console.log('Quick add event for date:', date);
    }

    handleSportWidgetClick(widget) {
        const sport = this.getSportFromWidget(widget);
        
        // Add visual feedback
        widget.classList.add('pulse');
        setTimeout(() => {
            widget.classList.remove('pulse');
        }, 600);
        
        // Filter events by sport
        this.filterBySport(sport);
        
        console.log('Sport widget clicked:', sport);
    }

    getSportFromWidget(widget) {
        const classes = widget.classList;
        if (classes.contains('running')) return 'running';
        if (classes.contains('cycling')) return 'cycling';
        if (classes.contains('swimming')) return 'swimming';
        if (classes.contains('trail_running')) return 'trail_running';
        if (classes.contains('triathlon')) return 'triathlon';
        if (classes.contains('duathlon')) return 'duathlon';
        return 'other';
    }

    filterBySport(sport) {
        document.querySelectorAll('.event-card').forEach(event => {
            const eventSport = this.getSportFromEventCard(event);
            
            if (sport === 'all' || eventSport === sport) {
                event.style.opacity = '1';
                event.style.transform = 'scale(1)';
            } else {
                event.style.opacity = '0.3';
                event.style.transform = 'scale(0.95)';
            }
        });

        // Update URL parameters
        const url = new URL(window.location);
        if (sport !== 'all') {
            url.searchParams.set('sport_filter', sport);
        } else {
            url.searchParams.delete('sport_filter');
        }
        
        // Update browser history without page reload
        window.history.pushState({}, '', url);
    }

    setupAnimations() {
        // Intersection Observer for fade-in animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        // Observe sport widgets
        document.querySelectorAll('.sport-widget').forEach(widget => {
            widget.classList.add('fade-in');
            observer.observe(widget);
        });

        // Stagger animation for calendar days
        document.querySelectorAll('.calendar-day').forEach((day, index) => {
            if (!day.classList.contains('calendar-day-empty')) {
                day.style.animationDelay = `${index * 20}ms`;
                day.classList.add('fade-in');
                observer.observe(day);
            }
        });
    }

    initializeTooltips() {
        // Tooltips disabled for cleaner look
    }

    setupKeyboardNavigation() {
        // Make calendar days focusable
        document.querySelectorAll('.calendar-day').forEach(day => {
            if (!day.classList.contains('calendar-day-empty')) {
                day.setAttribute('tabindex', '0');
                
                day.addEventListener('focus', () => {
                    this.selectDay(day);
                });
            }
        });
    }

    changeView(button) {
        const view = button.textContent.toLowerCase().trim();
        this.currentView = view;
        
        // Add loading state
        this.setLoading(true);
        
        // Clear current selection
        this.clearSelection();
        
        console.log('Changed view to:', view);
    }

    navigatePrevious() {
        const prevButton = document.querySelector('.fa-chevron-left').closest('a');
        if (prevButton) {
            this.setLoading(true);
            window.location.href = prevButton.href;
        }
    }

    navigateNext() {
        const nextButton = document.querySelector('.fa-chevron-right').closest('a');
        if (nextButton) {
            this.setLoading(true);
            window.location.href = nextButton.href;
        }
    }

    clearSelection() {
        // Clear all selections
        document.querySelectorAll('.calendar-day').forEach(day => {
            day.classList.remove('calendar-day-selected', 'week-day-selected');
        });
        
        this.selectedDate = null;
        this.selectedElement = null;
        
        // Clear sport filter
        this.filterBySport('all');
    }

    setLoading(isLoading) {
        this.isLoading = isLoading;
        const calendarContainer = document.querySelector('.calendar-month, .calendar-week-view');
        
        if (calendarContainer) {
            if (isLoading) {
                calendarContainer.classList.add('loading');
                calendarContainer.style.opacity = '0.7';
            } else {
                calendarContainer.classList.remove('loading');
                calendarContainer.style.opacity = '1';
            }
        }
    }

    handleResize() {
        // Update responsive layout
        this.updateResponsiveLayout();
        
        // Reapply event colors after resize
        this.applyEventColors();
    }

    updateResponsiveLayout() {
        const isMobile = window.innerWidth < 768;
        
        if (isMobile) {
            // Adjust for mobile
            document.querySelectorAll('.sport-widget').forEach(widget => {
                widget.style.marginBottom = '15px';
            });
        }
    }

    showQuickAddModal(date) {
        // Create and show a quick add event modal
        const modal = this.createQuickAddModal(date);
        document.body.appendChild(modal);
        
        // Show modal (using Bootstrap if available)
        if (typeof $ !== 'undefined' && $.fn.modal) {
            $(modal).modal('show');
            
            // Remove modal when hidden
            $(modal).on('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        } else {
            // Fallback: show modal manually
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }

// Keep your original createQuickAddModal function unchanged
createQuickAddModal(date) {
    // Only disable modal for coaches if they're NOT viewing a specific athlete
    if ((currentUserView === 'coach' || userRole === 'coach') && !viewingAthleteId) {
        // Coach is on overview calendar - disable modal
        console.log('Quick modal disabled for coaches on overview calendar');
        return;
    }
    
    // CLEAN: Build URLs with proper parameter handling
    let sessionUrl = `${urls.sessionCreate}?date=${date}`;
    let raceUrl = `${urls.raceCreate}?date=${date}`;
    let customUrl = `${urls.customEventCreate}?date=${date}`;
    
    // Add athlete parameter only if we have a valid athlete ID
    if (viewingAthleteId && typeof viewingAthleteId === 'number' && viewingAthleteId > 0) {
        sessionUrl += `&athlete=${viewingAthleteId}`;
        raceUrl += `&athlete=${viewingAthleteId}`;
        customUrl += `&athlete=${viewingAthleteId}`;
    }
    
    // Debug
    console.log('🔗 Session URL:', sessionUrl);
    
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add Event - ${date}</h5>
                    <button type="button" class="close" data-dismiss="modal" onclick="this.closest('.modal').remove()">
                        <span>&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="btn-group-vertical w-100">
                        <a href="${sessionUrl}" class="btn btn-success mb-2">
                            <i class="fas fa-running"></i> Training Session
                        </a>
                        <a href="${raceUrl}" class="btn btn-warning mb-2">
                            <i class="fas fa-trophy"></i> Race Event
                        </a>
                        <a href="${customUrl}" class="btn btn-info">
                            <i class="fas fa-star"></i> Custom Event
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    return modal;
}

    showEventDetails(eventElement) {
        // Extract event data
        const title = eventElement.querySelector('.event-title')?.textContent || 'Event';
        const time = eventElement.querySelector('.event-time')?.textContent || '';
        const duration = eventElement.querySelector('.event-duration')?.textContent || '';
        const eventId = eventElement.getAttribute('data-event-id');
        
        console.log('Show event details:', { title, time, duration, eventId });
        
        // You can implement a detailed event modal here
        // For now, just try alternative navigation
        const actionLink = eventElement.querySelector('.event-actions a');
        if (actionLink) {
            window.location.href = actionLink.href;
        } else {
            alert(`Event: ${title}\nTime: ${time}\nDuration: ${duration}`);
        }
    }

    showSportDetails(widget) {
        // Show additional sport statistics on hover
        const sport = this.getSportFromWidget(widget);
        const details = this.getSportDetails(sport);
        
        // Create or update details tooltip
        this.showSportTooltip(widget, details);
    }

    hideSportDetails() {
        // Hide sport details tooltip
        const existingTooltip = document.querySelector('.sport-tooltip');
        if (existingTooltip) {
            existingTooltip.remove();
        }
    }

    getSportDetails(sport) {
        // Return detailed statistics for the sport
        return {
            avgDuration: '45 minutes',
            longestSession: '2h 30m',
            totalDistance: sport === 'running' ? '125 km' : sport === 'cycling' ? '450 km' : 'N/A',
            improvement: '+12%'
        };
    }

    showSportTooltip(widget, details) {
        const tooltip = document.createElement('div');
        tooltip.className = 'sport-tooltip position-absolute bg-dark text-white p-2 rounded';
        tooltip.style.cssText = 'z-index: 1000; font-size: 12px; max-width: 200px;';
        
        tooltip.innerHTML = `
            <div>Avg Duration: ${details.avgDuration}</div>
            <div>Longest: ${details.longestSession}</div>
            <div>Distance: ${details.totalDistance}</div>
            <div>Improvement: ${details.improvement}</div>
        `;
        
        // Position tooltip
        const rect = widget.getBoundingClientRect();
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
        
        document.body.appendChild(tooltip);
    }

    onDateSelected(date, element) {
        // Custom event handling
        const event = new CustomEvent('dateSelected', {
            detail: { date, element, view: this.currentView }
        });
        document.dispatchEvent(event);
    }

    validateProgressBars() {
        // Validate and fix any invalid progress bar values
        document.querySelectorAll('.progress-bar').forEach(bar => {
            const currentWidth = bar.style.width;
            const widthValue = parseFloat(currentWidth);
            
            // Validate and constrain the value
            if (isNaN(widthValue) || widthValue < 0) {
                bar.style.width = '0%';
            } else if (widthValue > 100) {
                bar.style.width = '100%';
            }
            
            // Add animation class
            bar.classList.add('progress-bar-animated');
        });
    }

    // Public API methods
    getSelectedDate() {
        return this.selectedDate;
    }

    selectDate(date) {
        // Find and select the day with the given date
        const dayElement = document.querySelector(`[data-date="${date}"]`);
        
        if (dayElement) {
            this.selectDay(dayElement);
        }
    }

    refreshCalendar() {
        this.setLoading(true);
        // Reload current page or fetch new data
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Create global calendar instance
    window.calendar = new EnhancedCalendar();
    
    // Add custom event listeners
    document.addEventListener('dateSelected', function(e) {
        console.log('Date selected event:', e.detail);
    });
    
    // Initialize any additional features
    initializeAdditionalFeatures();
});

function initializeAdditionalFeatures() {
    // Initialize drag and drop for events (if needed)
    initializeDragDrop();
    
    // Initialize context menus
    initializeContextMenus();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
}

function initializeDragDrop() {
    // Add drag and drop functionality for moving events
    document.querySelectorAll('.event-card').forEach(event => {
        event.draggable = true;
        
        event.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', this.textContent);
            e.dataTransfer.setData('event-id', this.getAttribute('data-event-id'));
            this.style.opacity = '0.5';
        });
        
        event.addEventListener('dragend', function(e) {
            this.style.opacity = '1';
        });
    });
    
    // Add drop zones
    document.querySelectorAll('.calendar-day').forEach(day => {
        day.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        day.addEventListener('dragleave', function(e) {
            this.classList.remove('drag-over');
        });
        
        day.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const eventId = e.dataTransfer.getData('event-id');
            const newDate = window.calendar.getDateFromDay(this);
            
            if (eventId && newDate) {
                moveEvent(eventId, newDate);
            }
        });
    });
}

function initializeContextMenus() {
    // Add right-click context menus
    document.querySelectorAll('.calendar-day').forEach(day => {
        day.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            showContextMenu(e, this);
        });
    });
}

function initializeKeyboardShortcuts() {
    // Add additional keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'n':
                    e.preventDefault();
                    // Open new event modal
                    if (window.calendar.selectedElement) {
                        window.calendar.quickAddEvent(window.calendar.selectedElement);
                    }
                    break;
                case 'r':
                    e.preventDefault();
                    window.calendar.refreshCalendar();
                    break;
            }
        }
    });
}

function showContextMenu(event, dayElement) {
    // Create and show context menu
    const menu = document.createElement('div');
    menu.className = 'context-menu position-absolute bg-white border rounded shadow';
    menu.style.cssText = 'z-index: 1000; min-width: 150px;';
    
    const date = window.calendar.getDateFromDay(dayElement);
    
    menu.innerHTML = `
        <div class="list-group list-group-flush">
            <a href="${urls.sessionCreate}?date=${date}" class="list-group-item list-group-item-action">
                <i class="fas fa-running"></i> Add Training
            </a>
            <a href="${urls.raceCreate}?date=${date}" class="list-group-item list-group-item-action">
                <i class="fas fa-trophy"></i> Add Race
            </a>
            <a href="${urls.customEventCreate}?date=${date}" class="list-group-item list-group-item-action">
                <i class="fas fa-star"></i> Add Custom Event
            </a>
            <a href="#" class="list-group-item list-group-item-action" onclick="window.calendar.selectDate('${date}')">
                <i class="fas fa-mouse-pointer"></i> Select Date
            </a>
        </div>
    `;
    
    // Position menu
    menu.style.left = event.pageX + 'px';
    menu.style.top = event.pageY + 'px';
    
    document.body.appendChild(menu);
    
    // Remove menu on click outside
    setTimeout(() => {
        document.addEventListener('click', function removeMenu() {
            if (menu.parentNode) {
                menu.parentNode.removeChild(menu);
            }
            document.removeEventListener('click', removeMenu);
        });
    }, 0);
}

function moveEvent(eventId, newDate) {
    // Handle moving event to new date
    console.log(`Moving event ${eventId} to ${newDate}`);
    
    // Make AJAX request to update event
    fetch('/api/events/move/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            event_id: eventId,
            new_date: newDate
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh calendar or update UI
            window.calendar.refreshCalendar();
        } else {
            alert('Failed to move event');
        }
    })
    .catch(error => {
        console.error('Error moving event:', error);
    });
}

function getCsrfToken() {
    // Get CSRF token for Django requests
    const csrfCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    
    return csrfCookie ? csrfCookie.split('=')[1] : '';
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EnhancedCalendar, CalendarUtils };
}