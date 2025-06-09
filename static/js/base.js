/**
 * Base JavaScript for the Application
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Base JavaScript loaded');
    
    // Initialize any global functionality here
    initializeTooltips();
    initializeNavigation();
});

/**
 * Initialize Bootstrap tooltips if they exist
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Initialize navigation enhancements
 */
function initializeNavigation() {
    // Add smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Highlight active navigation items
    highlightActiveNavItem();
}

/**
 * Highlight the current active navigation item
 */
function highlightActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        }
    });
}

$(document).ready(function() {
    // Initialize view toggle functionality
    initViewToggle();
});

/**
 * Check if current page is VMA calculator or other pages that don't need view reload
 */
function isViewIndependentPage() {
    const currentPath = window.location.pathname;
    const viewIndependentPages = [
        '/vma-calculator/',
        '/vma_calculator/',
        'vma-calculator',
        'vma_calculator'
    ];
    
    return viewIndependentPages.some(page => currentPath.includes(page));
}

/**
 * Initialize view toggle button functionality
 */
function initViewToggle() {
    // Handle view toggle button clicks
    $('.view-toggle-btn').on('click', function() {
        const viewMode = $(this).data('view');
        const currentActive = $('.view-toggle-btn.active').data('view');
        
        // Don't do anything if clicking the already active button
        if (viewMode === currentActive) {
            return;
        }
        
        // Show loading state
        const $btn = $(this);
        showButtonLoading($btn);
        
        // Submit form via AJAX
        switchView(viewMode, $btn);
    });
}

/**
 * Show loading state on button
 * @param {jQuery} $btn - Button element
 */
function showButtonLoading($btn) {
    const originalHtml = $btn.html();
    $btn.data('original-html', originalHtml);
    $btn.html('<i class="fas fa-spinner fa-spin"></i>');
    $btn.prop('disabled', true);
}

/**
 * Restore button from loading state
 * @param {jQuery} $btn - Button element
 */
function restoreButtonLoading($btn) {
    const originalHtml = $btn.data('original-html');
    $btn.html(originalHtml);
    $btn.prop('disabled', false);
    $btn.removeData('original-html');
}

/**
 * Switch view via AJAX
 * @param {string} viewMode - 'coach' or 'athlete'
 * @param {jQuery} $btn - Button that was clicked
 */
function switchView(viewMode, $btn) {
    $.ajax({
        url: '/switch-view/', // Make sure this matches your URL pattern
        method: 'POST',
        data: {
            'view_mode': viewMode,
            'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if (response.success) {
                // Update button states
                $('.view-toggle-btn').removeClass('active');
                $btn.addClass('active');
                
                // Update view indicator in navbar
                updateViewIndicator(viewMode);
                
                // Check if this is a view-independent page (like VMA calculator)
                if (isViewIndependentPage()) {
                    // Don't reload the page, just update the UI
                    showMessage(`Switched to ${viewMode} view`, 'success');
                    
                    // Update any view-specific data without reloading
                    updateViewSpecificData(viewMode);
                } else {
                    // Reload page to update content after a short delay for other pages
                    setTimeout(function() {
                        window.location.reload();
                    }, 800);
                }
            } else {
                showMessage(response.error || 'Failed to switch view. Please try again.', 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('View switch error:', error);
            showMessage('Error switching view. Please try again.', 'error');
        },
        complete: function() {
            // Restore button state
            restoreButtonLoading($btn);
        }
    });
}

/**
 * Update view-specific data without page reload
 * @param {string} viewMode - 'coach' or 'athlete'
 */
function updateViewSpecificData(viewMode) {
    // Update VMA data if on VMA calculator page
    const vmaDataElement = document.getElementById('vma-data');
    if (vmaDataElement) {
        vmaDataElement.dataset.currentView = viewMode;
        
        // If switching to athlete view and there's no selected athlete, 
        // we might want to update some UI elements
        if (viewMode === 'athlete') {
            vmaDataElement.dataset.selectedAthleteId = '';
            vmaDataElement.dataset.selectedAthleteName = '';
        }
        
        console.log(`Updated VMA calculator for ${viewMode} view`);
    }
    
    // Update any other view-dependent elements on the page
    updatePageTitleForView(viewMode);
}

/**
 * Update page title or other UI elements for the current view
 * @param {string} viewMode - 'coach' or 'athlete'
 */
function updatePageTitleForView(viewMode) {
    // You can add logic here to update page title, breadcrumbs, or other UI elements
    // For VMA calculator, we might want to keep it the same regardless of view
    const pageTitle = document.querySelector('h1, .page-title');
    if (pageTitle && pageTitle.textContent.includes('VMA Calculator')) {
        // Keep the same title - VMA calculator works the same for both views
        console.log(`VMA Calculator view updated to ${viewMode} - interface remains the same`);
    }
}

/**
 * Update the view indicator in the navbar
 * @param {string} viewMode - 'coach' or 'athlete'
 */
function updateViewIndicator(viewMode) {
    const $indicator = $('.navbar-text');
    const icon = viewMode === 'coach' ? 'users' : 'user';
    const viewName = viewMode.charAt(0).toUpperCase() + viewMode.slice(1);
    
    $indicator.html(`
        <i class="fas fa-${icon}"></i>
        ${viewName} View
        <span class="view-indicator">${viewMode.toUpperCase()}</span>
    `);
}

/**
 * Show alert message to user
 * @param {string} message - Message to display
 * @param {string} type - 'success' or 'error'
 */
function showMessage(message, type) {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const iconClass = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="${iconClass} mr-2"></i>
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;
    
    // Remove existing alerts and add new one
    $('.alert').remove();
    $('.container-fluid').prepend(alertHtml);
    
    // Auto-hide after 3 seconds for view switches (shorter than errors)
    const autoHideDelay = type === 'success' ? 3000 : 4000;
    setTimeout(function() {
        $('.alert').fadeOut(500, function() {
            $(this).remove();
        });
    }, autoHideDelay);
}

/**
 * Handle keyboard shortcuts for view switching (optional)
 * Ctrl+Shift+C for Coach view, Ctrl+Shift+A for Athlete view
 */
function initViewKeyboardShortcuts() {
    $(document).on('keydown', function(e) {
        // Only for coaches
        if (!$('.view-toggle-btn').length) return;
        
        if (e.ctrlKey && e.shiftKey) {
            if (e.keyCode === 67) { // C key
                e.preventDefault();
                $('.view-toggle-btn[data-view="coach"]').click();
            } else if (e.keyCode === 65) { // A key
                e.preventDefault();
                $('.view-toggle-btn[data-view="athlete"]').click();
            }
        }
    });
}