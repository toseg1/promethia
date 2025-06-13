/**
 * REUSABLE FORM ERROR STYLING JAVASCRIPT
 * Add this to your base.html or create a separate JS file
 * This will automatically style ALL your Django forms
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 Loading custom form styling...');
    
    // ========================================
    // AUTOMATIC ERROR STYLING
    // ========================================
    
    /**
     * Automatically add 'is-invalid' class to form controls with errors
     */
    function styleFormErrors() {
        const errorDivs = document.querySelectorAll('.invalid-feedback, .text-danger, .error');
        
        errorDivs.forEach(function(errorDiv) {
            // Find the closest form control
            let formControl = null;
            
            // Try different parent relationships
            const inputGroup = errorDiv.closest('.input-group');
            const formGroup = errorDiv.closest('.form-group, .mb-3, .col-md-6, .col-md-4');
            
            if (inputGroup) {
                formControl = inputGroup.querySelector('.form-control, .form-select, select, input, textarea');
            } else if (formGroup) {
                formControl = formGroup.querySelector('.form-control, .form-select, select, input, textarea');
            } else {
                // Look for siblings
                formControl = errorDiv.previousElementSibling;
                if (!formControl || !formControl.matches('.form-control, .form-select, select, input, textarea')) {
                    formControl = errorDiv.parentElement.querySelector('.form-control, .form-select, select, input, textarea');
                }
            }
            
            if (formControl) {
                formControl.classList.add('is-invalid');
                console.log('✅ Added error styling to:', formControl.name || formControl.id || 'unnamed field');
                
                // Add shake animation
                formControl.style.animation = 'shake 0.6s ease-in-out';
                
                // Add slide-down animation to error message
                if (errorDiv.classList.contains('invalid-feedback')) {
                    errorDiv.style.animation = 'slideDown 0.3s ease-out';
                }
            }
        });
    }
    
    // ========================================
    // ENHANCED FORM INTERACTIONS
    // ========================================
    
    /**
     * Add focus enhancement effects
     */
    function addFocusEffects() {
        const formControls = document.querySelectorAll('.form-control, .form-select, select, input, textarea');
        
        formControls.forEach(function(control) {
            // Focus effect
            control.addEventListener('focus', function() {
                const parent = this.closest('.input-group') || this.parentElement;
                parent.style.transform = 'scale(1.02)';
                parent.style.transition = 'transform 0.2s ease';
                parent.style.zIndex = '10';
            });
            
            // Blur effect
            control.addEventListener('blur', function() {
                const parent = this.closest('.input-group') || this.parentElement;
                parent.style.transform = 'scale(1)';
                parent.style.zIndex = '1';
            });
            
            // Clear error state on input
            control.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                    
                    // Hide error message with fade out
                    const errorDiv = this.parentElement.querySelector('.invalid-feedback') ||
                                   this.closest('.form-group, .mb-3, .input-group').querySelector('.invalid-feedback');
                    
                    if (errorDiv) {
                        errorDiv.style.animation = 'fadeOut 0.3s ease-out';
                        setTimeout(() => {
                            errorDiv.style.display = 'none';
                        }, 300);
                    }
                }
            });
        });
    }
    
    // ========================================
    // ALERT ENHANCEMENTS
    // ========================================
    
    /**
     * Auto-dismiss alerts and add animations
     */
    function enhanceAlerts() {
        const alerts = document.querySelectorAll('.alert');
        
        alerts.forEach(function(alert) {
            // Add fade-in animation
            alert.style.animation = 'fadeIn 0.5s ease-out';
            
            // Auto-dismiss after 8 seconds (if it has a close button)
            if (alert.querySelector('.close, [data-dismiss="alert"]')) {
                setTimeout(function() {
                    const closeBtn = alert.querySelector('.close, [data-dismiss="alert"]');
                    if (closeBtn && alert.parentElement) {
                        closeBtn.click();
                    }
                }, 8000);
            }
        });
    }
    
    // ========================================
    // BUTTON ENHANCEMENTS
    // ========================================
    
    /**
     * Add loading states and enhanced hover effects
     */
    function enhanceButtons() {
        const submitButtons = document.querySelectorAll('button[type="submit"], input[type="submit"]');
        
        submitButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                // Add loading state
                const originalText = this.innerHTML || this.value;
                const loadingText = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
                
                if (this.tagName === 'BUTTON') {
                    this.innerHTML = loadingText;
                } else {
                    this.value = 'Loading...';
                }
                
                this.disabled = true;
                
                // Re-enable after 3 seconds (in case form doesn't submit)
                setTimeout(() => {
                    if (this.tagName === 'BUTTON') {
                        this.innerHTML = originalText;
                    } else {
                        this.value = originalText;
                    }
                    this.disabled = false;
                }, 3000);
            });
        });
    }
    
    // ========================================
    // FORM VALIDATION ENHANCEMENT
    // ========================================
    
    /**
     * Add real-time validation feedback
     */
    function addRealTimeValidation() {
        const emailFields = document.querySelectorAll('input[type="email"], input[name*="email"]');
        const passwordFields = document.querySelectorAll('input[type="password"]');
        
        // Email validation
        emailFields.forEach(function(field) {
            field.addEventListener('blur', function() {
                const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
                
                if (this.value && !emailRegex.test(this.value)) {
                    this.classList.add('is-invalid');
                    showFieldError(this, 'Please enter a valid email address.');
                } else {
                    this.classList.remove('is-invalid');
                    hideFieldError(this);
                }
            });
        });
        
        // Password confirmation validation
        const passwordConfirmFields = document.querySelectorAll(
            'input[name="password2"], input[name="confirm_password"], input[name*="confirm"]'
        );
        
        passwordConfirmFields.forEach(function(confirmField) {
            confirmField.addEventListener('input', function() {
                const passwordField = document.querySelector('input[name="password1"], input[name="password"]');
                
                if (passwordField && this.value && passwordField.value !== this.value) {
                    this.classList.add('is-invalid');
                    showFieldError(this, 'Passwords do not match.');
                } else {
                    this.classList.remove('is-invalid');
                    hideFieldError(this);
                }
            });
        });
    }
    
    /**
     * Show field error message
     */
    function showFieldError(field, message) {
        hideFieldError(field); // Remove existing error first
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        errorDiv.style.animation = 'slideDown 0.3s ease-out';
        
        const parent = field.closest('.input-group') || field.parentElement;
        parent.appendChild(errorDiv);
    }
    
    /**
     * Hide field error message
     */
    function hideFieldError(field) {
        const parent = field.closest('.input-group') || field.parentElement;
        const existingError = parent.querySelector('.invalid-feedback');
        
        if (existingError) {
            existingError.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                if (existingError.parentElement) {
                    existingError.remove();
                }
            }, 300);
        }
    }
    
    // ========================================
    // ACCESSIBILITY ENHANCEMENTS
    // ========================================
    
    /**
     * Add ARIA attributes for better accessibility
     */
    function enhanceAccessibility() {
        const invalidFields = document.querySelectorAll('.is-invalid');
        
        invalidFields.forEach(function(field) {
            field.setAttribute('aria-invalid', 'true');
            
            const errorDiv = field.parentElement.querySelector('.invalid-feedback') ||
                           field.closest('.form-group, .mb-3').querySelector('.invalid-feedback');
            
            if (errorDiv) {
                const errorId = 'error-' + (field.name || field.id || Math.random().toString(36).substr(2, 9));
                errorDiv.id = errorId;
                field.setAttribute('aria-describedby', errorId);
            }
        });
    }
    
    // ========================================
    // INITIALIZE ALL ENHANCEMENTS
    // ========================================
    
    // Apply all enhancements
    styleFormErrors();
    addFocusEffects();
    enhanceAlerts();
    enhanceButtons();
    addRealTimeValidation();
    enhanceAccessibility();
    
    console.log('✨ Form styling and enhancements loaded successfully!');
    
    // Re-apply styling if new content is added dynamically
    const observer = new MutationObserver(function(mutations) {
        let hasNewErrors = false;
        
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    if (node.querySelector && node.querySelector('.invalid-feedback, .text-danger, .error')) {
                        hasNewErrors = true;
                    }
                }
            });
        });
        
        if (hasNewErrors) {
            console.log('🔄 New errors detected, re-applying styling...');
            styleFormErrors();
            enhanceAccessibility();
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Add fade out animation keyframe
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeOut {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(-10px); }
        }
    `;
    document.head.appendChild(style);
});