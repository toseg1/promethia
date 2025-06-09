// static/js/calendar_coach.js

$(document).ready(function() {
    initializeCoachCalendar();
});

function initializeCoachCalendar() {
    // Athlete filter functionality
    $('#athleteFilter').on('change', function() {
        var selectedAthlete = $(this).val();
        updateCalendarView(selectedAthlete);
    });
    
    // Quick athlete selection from athlete cards
    $('.athlete-quick-card').on('click', function() {
        var athleteId = $(this).data('athlete-id');
        if (athleteId) {
            updateCalendarView(athleteId);
        }
    });
    
    // Bulk actions for multiple athletes
    $('#bulkActionBtn').on('click', function() {
        showBulkActionModal();
    });
    
    // Event creation with pre-selected athlete
    $('.dropdown-menu a[href*="create"]').on('click', function(e) {
        var href = $(this).attr('href');
        var selectedAthlete = $('#athleteFilter').val();
        
        if (selectedAthlete && selectedAthlete !== 'all') {
            e.preventDefault();
            var separator = href.includes('?') ? '&' : '?';
            window.location.href = href + separator + 'athlete=' + selectedAthlete;
        }
    });
    
    // Initialize athlete statistics
    loadAthleteStatistics();
    
    // Auto-refresh functionality (every 5 minutes)
    setInterval(function() {
        refreshCalendarData();
    }, 300000);
}

function updateCalendarView(athleteId) {
    var currentUrl = new URL(window.location.href);
    
    if (athleteId === 'all') {
        currentUrl.searchParams.delete('athlete');
    } else {
        currentUrl.searchParams.set('athlete', athleteId);
    }
    
    // Show loading indicator
    showLoadingIndicator();
    
    // Update URL and reload
    window.location.href = currentUrl.toString();
}

function loadAthleteStatistics() {
    var selectedAthlete = $('#athleteFilter').val();
    
    if (selectedAthlete && selectedAthlete !== 'all') {
        $.ajax({
            url: '/api/athlete/' + selectedAthlete + '/statistics/',
            method: 'GET',
            success: function(data) {
                updateAthleteStatsDisplay(data);
            },
            error: function() {
                console.error('Failed to load athlete statistics');
            }
        });
    }
}

function updateAthleteStatsDisplay(stats) {
    // Update various statistics displays
    if (stats.upcoming_sessions !== undefined) {
        $('.stat-upcoming-sessions').text(stats.upcoming_sessions);
    }
    
    if (stats.completion_rate !== undefined) {
        $('.stat-completion-rate').text(stats.completion_rate + '%');
        
        // Update progress bar color based on completion rate
        var progressBar = $('.completion-rate-progress');
        progressBar.removeClass('bg-success bg-warning bg-danger');
        
        if (stats.completion_rate >= 80) {
            progressBar.addClass('bg-success');
        } else if (stats.completion_rate >= 60) {
            progressBar.addClass('bg-warning');
        } else {
            progressBar.addClass('bg-danger');
        }
        
        progressBar.css('width', stats.completion_rate + '%');
    }
    
    if (stats.upcoming_races !== undefined) {
        $('.stat-upcoming-races').text(stats.upcoming_races);
    }
}

function showBulkActionModal() {
    var selectedAthletes = getSelectedAthletes();
    
    if (selectedAthletes.length === 0) {
        alert('Please select at least one athlete');
        return;
    }
    
    var modalContent = `
        <div class="modal fade" id="bulkActionModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Bulk Actions for ${selectedAthletes.length} athlete(s)</h5>
                        <button type="button" class="close" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label>Select Action:</label>
                            <select class="form-control" id="bulkActionType">
                                <option value="">Choose an action...</option>
                                <option value="create_session">Create Training Session</option>
                                <option value="create_race">Create Race Event</option>
                                <option value="send_message">Send Message</option>
                                <option value="export_data">Export Data</option>
                            </select>
                        </div>
                        <div id="bulkActionDetails" style="display: none;">
                            <!-- Dynamic content based on action type -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="executeBulkAction()">Execute</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(modalContent);
    $('#bulkActionModal').modal('show');
    
    // Remove modal when hidden
    $('#bulkActionModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
    
    // Handle action type change
    $('#bulkActionType').on('change', function() {
        var actionType = $(this).val();
        showBulkActionDetails(actionType);
    });
}

function showBulkActionDetails(actionType) {
    var detailsContainer = $('#bulkActionDetails');
    var content = '';
    
    switch (actionType) {
        case 'create_session':
            content = `
                <div class="form-group">
                    <label>Session Title:</label>
                    <input type="text" class="form-control" id="bulkSessionTitle" placeholder="Enter session title">
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label>Date:</label>
                            <input type="date" class="form-control" id="bulkSessionDate">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group">
                            <label>Time:</label>
                            <input type="time" class="form-control" id="bulkSessionTime">
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'send_message':
            content = `
                <div class="form-group">
                    <label>Message Subject:</label>
                    <input type="text" class="form-control" id="bulkMessageSubject" placeholder="Enter subject">
                </div>
                <div class="form-group">
                    <label>Message:</label>
                    <textarea class="form-control" id="bulkMessageContent" rows="4" placeholder="Enter your message"></textarea>
                </div>
            `;
            break;
            
        case 'export_data':
            content = `
                <div class="form-group">
                    <label>Export Type:</label>
                    <select class="form-control" id="bulkExportType">
                        <option value="sessions">Training Sessions</option>
                        <option value="races">Race Events</option>
                        <option value="all">All Data</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Date Range:</label>
                    <div class="row">
                        <div class="col-md-6">
                            <input type="date" class="form-control" id="bulkExportStartDate">
                        </div>
                        <div class="col-md-6">
                            <input type="date" class="form-control" id="bulkExportEndDate">
                        </div>
                    </div>
                </div>
            `;
            break;
    }
    
    if (content) {
        detailsContainer.html(content).show();
    } else {
        detailsContainer.hide();
    }
}

function getSelectedAthletes() {
    // Get currently selected athletes based on current view
    var selectedAthlete = $('#athleteFilter').val();
    
    if (selectedAthlete && selectedAthlete !== 'all') {
        return [selectedAthlete];
    }
    
    // If viewing all athletes, return all athlete IDs
    var athleteIds = [];
    $('.athlete-quick-card').each(function() {
        var athleteId = $(this).data('athlete-id');
        if (athleteId) {
            athleteIds.push(athleteId);
        }
    });
    
    return athleteIds;
}

function executeBulkAction() {
    var actionType = $('#bulkActionType').val();
    var selectedAthletes = getSelectedAthletes();
    
    if (!actionType) {
        alert('Please select an action type');
        return;
    }
    
    showLoadingIndicator();
    
    var requestData = {
        action_type: actionType,
        athlete_ids: selectedAthletes
    };
    
    // Add action-specific data
    switch (actionType) {
        case 'create_session':
            requestData.session_data = {
                title: $('#bulkSessionTitle').val(),
                date: $('#bulkSessionDate').val(),
                time: $('#bulkSessionTime').val()
            };
            break;
            
        case 'send_message':
            requestData.message_data = {
                subject: $('#bulkMessageSubject').val(),
                content: $('#bulkMessageContent').val()
            };
            break;
            
        case 'export_data':
            requestData.export_data = {
                type: $('#bulkExportType').val(),
                start_date: $('#bulkExportStartDate').val(),
                end_date: $('#bulkExportEndDate').val()
            };
            break;
    }
    
    $.ajax({
        url: '/api/bulk-actions/',
        method: 'POST',
        data: JSON.stringify(requestData),
        contentType: 'application/json',
        success: function(response) {
            hideLoadingIndicator();
            $('#bulkActionModal').modal('hide');
            
            if (response.success) {
                showSuccessMessage(response.message);
                
                // Refresh calendar if needed
                if (actionType === 'create_session' || actionType === 'create_race') {
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                }
            } else {
                showErrorMessage(response.message);
            }
        },
        error: function() {
            hideLoadingIndicator();
            showErrorMessage('Failed to execute bulk action');
        }
    });
}

function refreshCalendarData() {
    // Silently refresh calendar data without full page reload
    var currentParams = new URLSearchParams(window.location.search);
    
    $.ajax({
        url: '/calendar/api/events/?' + currentParams.toString(),
        method: 'GET',
        success: function(data) {
            updateCalendarEvents(data.events);
        },
        error: function() {
            console.error('Failed to refresh calendar data');
        }
    });
}

function updateCalendarEvents(events) {
    // Update calendar display with new event data
    // This would require more complex DOM manipulation
    // For simplicity, we'll just update event counts
    
    var eventCounts = {
        sessions: 0,
        races: 0,
        custom: 0
    };
    
    events.forEach(function(event) {
        if (event.type === 'session') {
            eventCounts.sessions++;
        } else if (event.type === 'race') {
            eventCounts.races++;
        } else if (event.type === 'custom') {
            eventCounts.custom++;
        }
    });
    
    // Update any visible counters
    $('.event-count-sessions').text(eventCounts.sessions);
    $('.event-count-races').text(eventCounts.races);
    $('.event-count-custom').text(eventCounts.custom);
}

function showLoadingIndicator() {
    if ($('#loadingIndicator').length === 0) {
        $('body').append(`
            <div id="loadingIndicator" class="loading-overlay">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin fa-3x"></i>
                    <p class="mt-2">Loading...</p>
                </div>
            </div>
        `);
    }
    $('#loadingIndicator').show();
}

function hideLoadingIndicator() {
    $('#loadingIndicator').hide();
}

function showSuccessMessage(message) {
    showAlert(message, 'success');
}

function showErrorMessage(message) {
    showAlert(message, 'danger');
}

function showAlert(message, type) {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        </div>
    `;
    
    $('.content .container-fluid').prepend(alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
}

// CSS for loading indicator (add to calendar.css)
const loadingCSS = `
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.loading-spinner {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    color: #007bff;
}
`;

// Add loading CSS to document if not already present
if (!document.getElementById('coach-calendar-styles')) {
    const style = document.createElement('style');
    style.id = 'coach-calendar-styles';
    style.textContent = loadingCSS;
    document.head.appendChild(style);
}