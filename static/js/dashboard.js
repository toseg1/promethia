// coach_dashboard.js
// JavaScript functionality for the coach dashboard

// Core functions for athlete selection
function handleAthleteSelection() {
    const select = document.getElementById('athlete-select');
    if (!select) {
        console.error('Athlete select element not found');
        return;
    }
    
    const selectedValue = select.value;
    console.log('Selected athlete:', selectedValue); // Debug log
    
    // Construct the URL with the selected athlete parameter
    const currentUrl = window.location.href.split('?')[0]; // Remove existing query params
    let newUrl = currentUrl;
    
    if (selectedValue !== 'all') {
        newUrl += '?athlete=' + selectedValue;
    }
    
    console.log('Redirecting to:', newUrl); // Debug log
    
    // Redirect to the new URL
    window.location.href = newUrl;
}

function selectAthlete(athleteId) {
    console.log('Selecting athlete:', athleteId); // Debug log
    const currentUrl = window.location.href.split('?')[0];
    const newUrl = currentUrl + '?athlete=' + athleteId;
    console.log('Redirecting to:', newUrl); // Debug log
    window.location.href = newUrl;
}

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize athlete selection dropdown
    initializeAthleteSelector();
    
    // Initialize athlete selection buttons
    initializeAthleteButtons();
    
    // Initialize tooltips if using Bootstrap
    if (typeof $().tooltip === 'function') {
        $('[title]').tooltip();
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    console.log('Coach dashboard loaded');
});

function initializeAthleteButtons() {
    // Use event delegation to handle athlete selection buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.select-athlete-btn')) {
            const button = e.target.closest('.select-athlete-btn');
            const athleteId = button.getAttribute('data-athlete-id');
            if (athleteId) {
                selectAthlete(athleteId);
            }
        }
    });
}

function removeAthleteRelationship(athleteId, athleteName) {
    // Show confirmation dialog
    if (confirm(`Are you sure you want to remove ${athleteName} from your coached athletes? This action cannot be undone.`)) {
        // Show loading state
        showLoadingState();
        
        // Make AJAX request to remove the relationship
        fetch(`/user-management/remove-athlete/${athleteId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'athlete_id': athleteId
            })
        })
        .then(response => {
            if (response.ok) {
                // Reload the page to refresh the athlete list
                window.location.reload();
            } else {
                throw new Error('Failed to remove athlete');
            }
        })
        .catch(error => {
            hideLoadingState();
            alert('Error removing athlete: ' + error.message);
            console.error('Error:', error);
        });
    }
}

function getCsrfToken() {
    // Get CSRF token from meta tag or cookie
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    // Fallback: get from cookie
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    return cookieValue || '';
}

function initializeAthleteSelector() {
    const athleteSelect = document.getElementById('athlete-select');
    if (athleteSelect) {
        // Add change event listener
        athleteSelect.addEventListener('change', function() {
            handleAthleteSelection();
        });
        
        // Add loading state functionality
        athleteSelect.addEventListener('change', function() {
            const selectedValue = this.value;
            
            // Show loading indicator
            showLoadingState();
        });
    }
}

function showLoadingState() {
    // Create and show a loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner-border text-primary" role="status">
                <span class="sr-only">Loading...</span>
            </div>
            <p class="mt-2">Loading athlete data...</p>
        </div>
    `;
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        flex-direction: column;
    `;
    
    document.body.appendChild(loadingOverlay);
}

function hideLoadingState() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// Utility function to update completion rate badges
function updateCompletionRateBadge(rate, element) {
    let badgeClass = 'badge-danger';
    if (rate >= 80) {
        badgeClass = 'badge-success';
    } else if (rate >= 60) {
        badgeClass = 'badge-warning';
    }
    
    element.className = `badge ${badgeClass}`;
    element.textContent = Math.round(rate) + '%';
}

// Function to refresh dashboard data via AJAX (optional enhancement)
function refreshDashboardData(athleteId = null) {
    const url = athleteId ? `?athlete=${athleteId}&ajax=1` : '?ajax=1';
    
    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update dashboard elements with new data
        updateDashboardElements(data);
    })
    .catch(error => {
        console.error('Error refreshing dashboard:', error);
    });
}

function updateDashboardElements(data) {
    // Update widgets with new data
    // This would be used if you implement AJAX refresh functionality
    
    // Example:
    // document.getElementById('total-sessions').textContent = data.total_sessions;
    // document.getElementById('completion-rate').textContent = data.completion_rate + '%';
}

// Enhanced athlete selection with smooth transitions
function selectAthleteWithTransition(athleteId) {
    // Add a smooth transition effect
    const mainContent = document.querySelector('.content-wrapper');
    if (mainContent) {
        mainContent.style.opacity = '0.5';
        mainContent.style.transition = 'opacity 0.3s ease';
    }
    
    // Show loading state
    showLoadingState();
    
    // Navigate to the new athlete view
    const currentUrl = window.location.href.split('?')[0];
    const newUrl = currentUrl + '?athlete=' + athleteId;
    window.location.href = newUrl;
}

// Add keyboard navigation support
document.addEventListener('keydown', function(e) {
    // ESC key to go back to all athletes view
    if (e.key === 'Escape') {
        const athleteSelect = document.getElementById('athlete-select');
        if (athleteSelect && athleteSelect.value !== 'all') {
            athleteSelect.value = 'all';
            handleAthleteSelection();
        }
    }
});

// Auto-refresh functionality (optional)
let autoRefreshInterval = null;

function startAutoRefresh(intervalMinutes = 5) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(() => {
        const athleteSelect = document.getElementById('athlete-select');
        const currentAthlete = athleteSelect ? athleteSelect.value : null;
        refreshDashboardData(currentAthlete !== 'all' ? currentAthlete : null);
    }, intervalMinutes * 60 * 1000);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Export functions for use in other scripts
window.CoachDashboard = {
    handleAthleteSelection: function() {
        if (typeof handleAthleteSelection === 'function') {
            handleAthleteSelection();
        }
    },
    selectAthlete: function(athleteId) {
        if (typeof selectAthlete === 'function') {
            selectAthlete(athleteId);
        } else {
            selectAthleteWithTransition(athleteId);
        }
    },
    refreshData: refreshDashboardData,
    startAutoRefresh: startAutoRefresh,
    stopAutoRefresh: stopAutoRefresh
};

document.addEventListener('click', function(e) {
    if (e.target.closest('.remove-athlete-btn')) {
        const button = e.target.closest('.remove-athlete-btn');
        const athleteId = button.getAttribute('data-athlete-id');
        const athleteName = button.getAttribute('data-athlete-name');
        if (athleteId && athleteName) {
            prepareRemoveAthleteModal(athleteId, athleteName);
        }
    }
    
    if (e.target && e.target.id === 'confirmRemoveAthlete') {
        handleRemoveAthleteConfirmation();
    }
});

document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'removalReason') {
        toggleOtherReasonField(e.target.value);
    }
});

// Add these new functions:
function prepareRemoveAthleteModal(athleteId, athleteName) {
    document.getElementById('athleteNameToRemove').textContent = athleteName;
    document.getElementById('athleteIdToRemove').value = athleteId;
    
    const form = document.getElementById('removeAthleteForm');
    form.action = `/remove-athlete/${athleteId}/`;
    
    document.getElementById('removalReason').value = '';
    document.getElementById('otherReason').value = '';
    toggleOtherReasonField('');
}

function toggleOtherReasonField(selectedValue) {
    const otherReasonGroup = document.getElementById('otherReasonGroup');
    if (selectedValue === 'other') {
        otherReasonGroup.style.display = 'block';
    } else {
        otherReasonGroup.style.display = 'none';
    }
}

function handleRemoveAthleteConfirmation() {
    const form = document.getElementById('removeAthleteForm');
    const confirmButton = document.getElementById('confirmRemoveAthlete');
    
    confirmButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Removing...';
    confirmButton.disabled = true;
    
    fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            $('#removeAthleteModal').modal('hide');
            window.location.reload();
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        confirmButton.innerHTML = '<i class="fas fa-user-times mr-1"></i> Remove Athlete';
        confirmButton.disabled = false;
        alert('Error: ' + error.message);
    });
}