/**
 * Race Form Management JavaScript
 */

// Global variables for race management
let editingRaceId = null;
let isSubmitting = false;

$(document).ready(function() {
    console.log('Race form JavaScript loaded');
    initializeRaceForm();
    
    // Create global utilities object for dashboard communication
    window.raceFormUtils = {
        openAddModal: openAddModal,
        openEditModal: openEditModal,
        resetForm: resetRaceForm,
        validateForm: validateForm
    };
    
    console.log('Race form utilities available globally');
});

/**
 * Initialize race form functionality
 */
function initializeRaceForm() {
    console.log('Initializing race form...');
    
    // Sport type change handler
    $('#sportType').on('change', function() {
        updateSportPreview();
    });
    
    // Form submission
    $('#raceForm').on('submit', function(e) {
        e.preventDefault();
        console.log('Form submitted');
        saveRace();
    });
    
    // Reset form when modal closes
    $('#addRaceModal').on('hidden.bs.modal', function() {
        resetRaceForm();
    });
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    $('#raceDate').attr('min', today);
    
    // Input validation on blur
    setupInputValidation();
    
    console.log('Race form initialized successfully');
}

/**
 * Setup real-time input validation
 */
function setupInputValidation() {
    const requiredFields = ['raceName', 'sportType', 'raceDate', 'raceLocation'];
    
    requiredFields.forEach(fieldId => {
        $(`#${fieldId}`).on('blur', function() {
            validateField($(this));
        });
        
        $(`#${fieldId}`).on('input', function() {
            if ($(this).hasClass('is-invalid')) {
                validateField($(this));
            }
        });
    });
    
    // Special validation for date
    $('#raceDate').on('change', function() {
        validateDateField();
    });
}

/**
 * Validate individual field
 */
function validateField($field) {
    const value = $field.val().trim();
    const isRequired = $field.prop('required');
    
    if (isRequired && !value) {
        $field.addClass('is-invalid').removeClass('is-valid');
        return false;
    } else {
        $field.removeClass('is-invalid').addClass('is-valid');
        return true;
    }
}

/**
 * Validate date field specifically
 */
function validateDateField() {
    const $dateField = $('#raceDate');
    const dateValue = $dateField.val();
    
    if (!dateValue) {
        $dateField.addClass('is-invalid').removeClass('is-valid');
        return false;
    }
    
    const raceDate = new Date(dateValue);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (raceDate < today) {
        $dateField.addClass('is-invalid').removeClass('is-valid');
        showValidationMessage('Race date cannot be in the past', 'error');
        return false;
    } else {
        $dateField.removeClass('is-invalid').addClass('is-valid');
        return true;
    }
}

/**
 * Update sport type preview
 */
function updateSportPreview() {
    const selectedOption = $('#sportType option:selected');
    const sportType = selectedOption.val();
    const icon = selectedOption.data('icon');
    const color = selectedOption.data('color');
    const text = selectedOption.text();
    
    if (sportType) {
        $('#sportPreview').show().addClass('show');
        $('.sport-preview-icon')
            .removeClass()
            .addClass('sport-preview-icon ' + icon + ' ' + color);
        $('.sport-preview-text').text(text);
        
        // Animate preview
        setTimeout(() => {
            $('#sportPreview').addClass('show');
        }, 100);
    } else {
        $('#sportPreview').hide().removeClass('show');
    }
    
    // Validate field if it was previously invalid
    if ($('#sportType').hasClass('is-invalid')) {
        validateField($('#sportType'));
    }
}

/**
 * Open add race modal (called by dashboard)
 */
function openAddModal() {
    console.log('Opening add race modal');
    editingRaceId = null;
    $('#modal-title').text('Add New Race');
    $('#save-btn-text').text('Save Race');
    resetRaceForm();
    $('#addRaceModal').modal('show');
    
    // Focus on first field after modal is shown
    $('#addRaceModal').one('shown.bs.modal', function() {
        $('#raceName').focus();
    });
}

/**
 * Open edit race modal (called by dashboard)
 */
function openEditModal(raceId) {
    console.log('Opening edit race modal for ID:', raceId);
    
    // Get race data from dashboard
    let race = null;
    if (window.dashboardRaceUtils && window.dashboardRaceUtils.getRaceById) {
        race = window.dashboardRaceUtils.getRaceById(raceId);
    }
    
    if (!race) {
        console.error('Race not found:', raceId);
        showValidationMessage('Race not found', 'error');
        return;
    }
    
    editingRaceId = raceId;
    $('#modal-title').text('Edit Race');
    $('#save-btn-text').text('Update Race');
    
    // Populate form with race data
    populateFormWithRace(race);
    
    $('#addRaceModal').modal('show');
}

/**
 * Populate form with race data
 */
function populateFormWithRace(race) {
    console.log('Populating form with race:', race);
    
    $('#raceName').val(race.name || '');
    $('#sportType').val(race.type || '');
    $('#raceDate').val(race.date || '');
    $('#raceTime').val(race.time || '');
    $('#raceDistance').val(race.distance || '');
    $('#raceLocation').val(race.location || '');
    $('#raceVenue').val(race.venue || '');
    $('#goalTime').val(race.goalTime || '');
    $('#goalType').val(race.goalType || '');
    $('#raceNotes').val(race.notes || '');
    
    // Update sport preview
    updateSportPreview();
    
    // Mark fields as valid if they have values
    $('#raceForm input, #raceForm select, #raceForm textarea').each(function() {
        if ($(this).val()) {
            $(this).removeClass('is-invalid').addClass('is-valid');
        }
    });
}

/**
 * Save race (add or update)
 */
function saveRace() {
    if (isSubmitting) {
        console.log('Already submitting, ignoring');
        return;
    }
    
    if (!validateForm()) {
        showValidationMessage('Please fix the errors before saving', 'error');
        return;
    }
    
    isSubmitting = true;
    console.log('Saving race...');
    
    const $saveBtn = $('#saveRaceBtn');
    $saveBtn.addClass('btn-loading').prop('disabled', true);
    
    const formData = collectFormData();
    console.log('Collected form data:', formData);
    
    // Simulate API call delay
    setTimeout(() => {
        console.log('Processing save...');
        
        // Call dashboard storage functions
        if (editingRaceId) {
            // Update existing race
            if (window.dashboardRaceUtils && window.dashboardRaceUtils.updateRaceInStorage) {
                window.dashboardRaceUtils.updateRaceInStorage(formData);
            } else {
                console.error('Dashboard update function not available');
                showValidationMessage('Error: Dashboard not connected', 'error');
            }
        } else {
            // Add new race
            if (window.dashboardRaceUtils && window.dashboardRaceUtils.addRaceToStorage) {
                window.dashboardRaceUtils.addRaceToStorage(formData);
            } else {
                console.error('Dashboard add function not available');
                showValidationMessage('Error: Dashboard not connected', 'error');
            }
        }
        
        // Close modal and reset form
        $('#addRaceModal').modal('hide');
        $saveBtn.removeClass('btn-loading').prop('disabled', false);
        isSubmitting = false;
        
    }, 1000);
}

/**
 * Collect form data
 */
function collectFormData() {
    return {
        id: editingRaceId || Date.now(),
        name: $('#raceName').val().trim(),
        type: $('#sportType').val(),
        date: $('#raceDate').val(),
        time: $('#raceTime').val(),
        distance: $('#raceDistance').val().trim(),
        location: $('#raceLocation').val().trim(),
        venue: $('#raceVenue').val().trim(),
        goalTime: $('#goalTime').val().trim(),
        goalType: $('#goalType').val(),
        notes: $('#raceNotes').val().trim(),
        createdAt: editingRaceId ? (function() {
            // Get existing creation date if editing
            const existingRace = window.dashboardRaceUtils && window.dashboardRaceUtils.getRaceById ? 
                                window.dashboardRaceUtils.getRaceById(editingRaceId) : null;
            return existingRace ? existingRace.createdAt : new Date().toISOString();
        })() : new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
}

/**
 * Validate entire form
 */
function validateForm() {
    let isValid = true;
    
    // Clear previous validation states
    $('.form-control').removeClass('is-invalid is-valid');
    
    // Required fields validation
    const requiredFields = [
        { id: 'raceName', message: 'Race name is required' },
        { id: 'sportType', message: 'Sport type is required' },
        { id: 'raceDate', message: 'Race date is required' },
        { id: 'raceLocation', message: 'Race location is required' }
    ];
    
    requiredFields.forEach(field => {
        const $field = $(`#${field.id}`);
        if (!validateField($field)) {
            isValid = false;
        }
    });
    
    // Date validation
    if (!validateDateField()) {
        isValid = false;
    }
    
    // Goal time format validation (optional)
    validateGoalTimeFormat();
    
    return isValid;
}

/**
 * Validate goal time format
 */
function validateGoalTimeFormat() {
    const goalTime = $('#goalTime').val().trim();
    if (goalTime) {
        // Check if format is like HH:MM:SS or MM:SS
        const timePattern = /^(\d{1,2}:)?([0-5]?\d):([0-5]?\d)$/;
        if (!timePattern.test(goalTime)) {
            $('#goalTime').addClass('is-invalid');
            showValidationMessage('Goal time format should be like 3:30:00 or 45:30', 'warning');
            return false;
        } else {
            $('#goalTime').removeClass('is-invalid').addClass('is-valid');
        }
    }
    return true;
}

/**
 * Reset form to initial state
 */
function resetRaceForm() {
    console.log('Resetting race form');
    $('#raceForm')[0].reset();
    $('.form-control').removeClass('is-invalid is-valid');
    $('#sportPreview').hide().removeClass('show');
    editingRaceId = null;
    isSubmitting = false;
    
    // Reset save button state
    $('#saveRaceBtn').removeClass('btn-loading').prop('disabled', false);
}

/**
 * Show validation message
 */
function showValidationMessage(message, type = 'info') {
    console.log('Validation message:', message, type);
    
    // Try to use dashboard's toast function first
    if (typeof showToast === 'function') {
        showToast(message, type);
    } else {
        // Fallback to simple alert
        alert(message);
    }
}