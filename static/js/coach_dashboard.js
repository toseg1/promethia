document.addEventListener('DOMContentLoaded', function() {
    initializeCoachDashboard();
});

/**
 * Initialize coach dashboard functionality
 */
function initializeCoachDashboard() {
    // Initialize athlete selection dropdown
    initializeAthleteSelection();
    
    // Initialize dashboard animations
    initializeDashboardAnimations();
    
    // Initialize tooltips and popovers
    initializeTooltips();
}

/**
 * Handle athlete selection dropdown functionality
 */
function initializeAthleteSelection() {
    const athleteSelect = document.getElementById('athlete-select');
    
    if (!athleteSelect) return;
    
    // Add loading state functionality
    athleteSelect.addEventListener('change', function() {
        showLoadingState();
        handleAthleteSelection();
    });
    
    // Add keyboard navigation
    athleteSelect.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            showLoadingState();
            handleAthleteSelection();
        }
    });
}

/**
 * Handle athlete selection and URL update
 */
function handleAthleteSelection() {
    const select = document.getElementById('athlete-select');
    const selectedValue = select.value;
    
    // Update URL to include the selected athlete
    const url = new URL(window.location);
    
    if (selectedValue === 'all') {
        url.searchParams.delete('athlete');
    } else {
        url.searchParams.set('athlete', selectedValue);
    }
    
    // Add smooth transition before reload
    document.body.style.opacity = '0.8';
    
    // Reload the page with the new parameters
    setTimeout(() => {
        window.location.href = url.toString();
    }, 200);
}

/**
 * Show loading state during athlete selection
 */
function showLoadingState() {
    const select = document.getElementById('athlete-select');
    const originalHTML = select.innerHTML;
    
    // Temporarily disable the select
    select.disabled = true;
    
    // Add loading indicator
    const loadingOption = document.createElement('option');
    loadingOption.value = '';
    loadingOption.textContent = 'Loading...';
    loadingOption.selected = true;
    
    select.innerHTML = '';
    select.appendChild(loadingOption);
    
    // Re-enable after a short delay (in case of network issues)
    setTimeout(() => {
        if (select.disabled) {
            select.disabled = false;
            select.innerHTML = originalHTML;
        }
    }, 5000);
}

/**
 * Initialize dashboard animations and transitions
 */
function initializeDashboardAnimations() {
    // Animate small boxes on load
    animateSmallBoxes();
    
    // Add hover effects to cards
    addCardHoverEffects();
    
    // Initialize table row animations
    initializeTableAnimations();
}

/**
 * Animate small info boxes
 */
function animateSmallBoxes() {
    const smallBoxes = document.querySelectorAll('.small-box');
    
    smallBoxes.forEach((box, index) => {
        box.style.opacity = '0';
        box.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            box.style.transition = 'all 0.3s ease';
            box.style.opacity = '1';
            box.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Add hover effects to cards
 */
function addCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
}

/**
 * Initialize table row animations
 */
function initializeTableAnimations() {
    const tableRows = document.querySelectorAll('table tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transition = 'background-color 0.2s ease';
            this.style.backgroundColor = 'rgba(0,123,255,0.05)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
}

/**
 * Initialize tooltips and popovers
 */
function initializeTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof $ !== 'undefined' && $.fn.tooltip) {
        $('[data-toggle="tooltip"]').tooltip();
    }
    
    // Add custom tooltips for completion rates
    addCompletionRateTooltips();
}

/**
 * Add tooltips for completion rates
 */
function addCompletionRateTooltips() {
    const completionBadges = document.querySelectorAll('.badge');
    
    completionBadges.forEach(badge => {
        if (badge.textContent.includes('%')) {
            const rate = parseInt(badge.textContent);
            let message = '';
            
            if (rate >= 80) {
                message = 'Excellent completion rate!';
            } else if (rate >= 60) {
                message = 'Good completion rate';
            } else {
                message = 'Needs improvement';
            }
            
            badge.setAttribute('title', message);
            badge.style.cursor = 'help';
        }
    });
}

/**
 * Utility function to refresh athlete data without full page reload
 */
function refreshAthleteData(athleteId) {
    const url = new URL(window.location);
    
    if (athleteId === 'all') {
        url.searchParams.delete('athlete');
    } else {
        url.searchParams.set('athlete', athleteId);
    }
    
    // You could implement AJAX refresh here instead of full page reload
    // For now, we'll use the simple approach
    window.location.href = url.toString();
}

/**
 * Handle dynamic content updates (if implementing AJAX)
 */
function updateDashboardContent(data) {
    // This function would be used if you implement AJAX updates
    // Update metrics
    updateMetrics(data.metrics);
    
    // Update tables
    updateTables(data.tables);
    
    // Update charts if any
    updateCharts(data.charts);
}

/**
 * Update metrics display
 */
function updateMetrics(metrics) {
    Object.keys(metrics).forEach(key => {
        const element = document.querySelector(`[data-metric="${key}"]`);
        if (element) {
            element.textContent = metrics[key];
        }
    });
}

/**
 * Update table content
 */
function updateTables(tables) {
    Object.keys(tables).forEach(tableId => {
        const table = document.getElementById(tableId);
        if (table) {
            const tbody = table.querySelector('tbody');
            if (tbody) {
                tbody.innerHTML = tables[tableId];
                initializeTableAnimations();
            }
        }
    });
}

/**
 * Update charts (placeholder for future chart implementation)
 */
function updateCharts(charts) {
    // Implement chart updates here if you add charts to the dashboard
    console.log('Chart updates not implemented yet');
}

/**
 * Handle errors gracefully
 */
function handleDashboardError(error) {
    console.error('Dashboard error:', error);
    
    // Show user-friendly error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-warning alert-dismissible fade show';
    errorDiv.innerHTML = `
        <strong>Notice:</strong> There was an issue loading some dashboard data. 
        <a href="#" onclick="window.location.reload()">Refresh the page</a> to try again.
        <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
        </button>
    `;
    
    const container = document.querySelector('.content-wrapper') || document.body;
    container.insertBefore(errorDiv, container.firstChild);
}

/**
 * Export functions for potential external use
 */
window.CoachDashboard = {
    handleAthleteSelection,
    refreshAthleteData,
    updateDashboardContent
};