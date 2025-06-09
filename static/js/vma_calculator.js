// VMA Calculator - Modified version with simplified results
// static/js/vma_calculator.js

// Function to get target time from the three inputs with fresh values
function getTargetTime() {
    const hoursInput = document.getElementById('targetHours');
    const minutesInput = document.getElementById('targetMinutes');
    const secondsInput = document.getElementById('targetSeconds');
    
    // Check if elements exist
    if (!hoursInput || !minutesInput || !secondsInput) {
        return null;
    }
    
    // Force fresh values from DOM
    const hours = parseInt(hoursInput.value || '0') || 0;
    const minutes = parseInt(minutesInput.value || '0') || 0;
    const seconds = parseInt(secondsInput.value || '0') || 0;
    
    // Debug logging
    console.log('Target time inputs:', { hours, minutes, seconds });
    
    // Validate ranges
    if (minutes > 59 || seconds > 59 || hours > 23) {
        return null;
    }
    
    // Check if at least minutes or seconds are provided
    if (hours === 0 && minutes === 0 && seconds === 0) {
        return null;
    }
    
    const totalSeconds = hours * 3600 + minutes * 60 + seconds;
    console.log('Calculated total seconds:', totalSeconds);
    
    return totalSeconds;
}

// Function to format target time for display
function formatTargetTimeForDisplay() {
    const hours = parseInt(document.getElementById('targetHours').value) || 0;
    const minutes = parseInt(document.getElementById('targetMinutes').value) || 0;
    const seconds = parseInt(document.getElementById('targetSeconds').value) || 0;
    
    if (hours === 0 && minutes === 0 && seconds === 0) {
        return null;
    }
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
}

function getVMAData() {
    const dataElement = document.getElementById('vma-data');
    if (!dataElement) return {};
    
    return {
        userVMA: dataElement.dataset.userVma ? parseFloat(dataElement.dataset.userVma) : null,
        currentView: dataElement.dataset.currentView || 'athlete',
        selectedAthlete: dataElement.dataset.selectedAthleteId ? {
            id: parseInt(dataElement.dataset.selectedAthleteId),
            name: dataElement.dataset.selectedAthleteName
        } : null
    };
}

// Global functions for template access
function useMyVMA() {
    const data = getVMAData();
    if (data.userVMA) {
        document.getElementById('vmaValue').value = data.userVMA;
        showNotification('MAS loaded: ' + data.userVMA + ' km/h', 'success');
    } else {
        showNotification('No MAS found in profile', 'warning');
    }
}

function setVMA(value) {
    document.getElementById('vmaValue').value = value;
    
    // Update visual state of VMA preset buttons
    document.querySelectorAll('.btn-group-toggle .preset-btn').forEach(btn => {
        btn.classList.remove('btn-secondary', 'active');
        btn.classList.add('btn-outline-secondary');
        
        if (btn.textContent.trim() === value.toString()) {
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-secondary', 'active');
        }
    });
}

function setDistance(value, unit) {
    // If no unit is specified, use the current unit from dropdown or default to meters
    if (!unit) {
        const distanceUnitElement = document.getElementById('distanceUnit');
        unit = distanceUnitElement ? distanceUnitElement.value : 'm';
    }
    
    document.getElementById('distance').value = value;
    document.getElementById('distanceUnit').value = unit;
    
    // Update the previousUnit data attribute to prevent unwanted conversions
    const distanceUnitElement = document.getElementById('distanceUnit');
    if (distanceUnitElement) {
        distanceUnitElement.dataset.previousUnit = unit;
    }
    
    // Update visual state of distance preset buttons
    document.querySelectorAll('.distance-presets .preset-btn').forEach(btn => {
        btn.classList.remove('btn-success', 'active');
        btn.classList.add('btn-outline-success');
        
        const btnText = btn.textContent.trim();
        let expectedText = '';
        
        if (unit === 'km' && value < 1) {
            expectedText = (value * 1000) + 'm';
        } else if (unit === 'km') {
            expectedText = value + 'km';
        } else {
            expectedText = value + unit;
        }
        
        if (btnText === expectedText) {
            btn.classList.remove('btn-outline-success');
            btn.classList.add('btn-success', 'active');
        }
    });
}

// New function to set distance based on common distances, respecting current unit
function setCommonDistance(distanceKm) {
    const currentUnit = document.getElementById('distanceUnit').value;
    let convertedDistance;
    
    // Convert from km to the current unit
    switch(currentUnit) {
        case 'm':
            convertedDistance = distanceKm * 1000;
            break;
        case 'miles':
            convertedDistance = distanceKm / 1.60934;
            break;
        case 'km':
        default:
            convertedDistance = distanceKm;
            break;
    }
    
    // Round appropriately based on unit
    if (currentUnit === 'm') {
        convertedDistance = Math.round(convertedDistance);
    } else {
        convertedDistance = Math.round(convertedDistance * 100) / 100;
    }
    
    setDistance(convertedDistance, currentUnit);
}

function clearForm() {
    document.getElementById('vmaCalculatorForm').reset();
    
    // Clear all input fields explicitly
    document.getElementById('vmaValue').value = '';
    document.getElementById('vmaPercentage').value = '';
    document.getElementById('distance').value = '';
    
    // Clear the time inputs specifically
    document.getElementById('targetHours').value = '';
    document.getElementById('targetMinutes').value = '';
    document.getElementById('targetSeconds').value = '';
    
    // Reset distance unit to default (m)
    document.getElementById('distanceUnit').value = 'm';
    document.getElementById('distanceUnit').dataset.previousUnit = 'm';
    
    // Hide results section
    document.getElementById('resultsSection').style.display = 'none';
    
    // Clear results content
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.innerHTML = '';
    }
    
    // Reset all preset button states
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.classList.remove('btn-secondary', 'btn-success', 'active');
        if (btn.parentElement.classList.contains('btn-group-toggle')) {
            btn.classList.add('btn-outline-secondary');
        } else {
            btn.classList.add('btn-outline-success');
        }
    });
    
    // Reset training zone highlights
    document.querySelectorAll('.training-zone').forEach(zone => {
        zone.style.backgroundColor = '#f8f9fa';
        zone.style.fontWeight = 'normal';
        zone.style.borderLeftWidth = '4px';
    });
    
    showNotification('Form cleared completely', 'info');
}

function parseTime(timeStr) {
    if (!timeStr) return null;
    const parts = timeStr.split(':').map(Number);
    if (parts.length === 2) {
        return parts[0] * 60 + parts[1];
    } else if (parts.length === 3) {
        return parts[0] * 3600 + parts[1] * 60 + parts[2];
    }
    return null;
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.round(seconds % 60);
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

function convertDistance(distance, fromUnit, toUnit) {
    const conversions = {
        'km': 1,
        'm': 0.001,
        'miles': 1.60934
    };
    
    const distanceInKm = distance * conversions[fromUnit];
    return distanceInKm / conversions[toUnit];
}

function calculateVMA() {
    // Clear previous results first to ensure fresh calculation
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    // Force fresh values from form elements
    const vmaValueElement = document.getElementById('vmaValue');
    const vmaPercentageElement = document.getElementById('vmaPercentage');
    const distanceElement = document.getElementById('distance');
    const distanceUnitElement = document.getElementById('distanceUnit');
    
    // Get fresh values, ensuring they're not cached
    const vmaValue = vmaValueElement ? parseFloat(vmaValueElement.value) : null;
    const vmaPercentage = vmaPercentageElement ? parseFloat(vmaPercentageElement.value) : null;
    const distance = distanceElement && distanceElement.value ? parseFloat(distanceElement.value) : null;
    const distanceUnit = distanceUnitElement ? distanceUnitElement.value : 'm';
    const targetTimeSeconds = getTargetTime();

    // Debug logging to verify fresh values
    console.log('Fresh calculation values:', {
        vmaValue,
        vmaPercentage,
        distance,
        distanceUnit,
        targetTimeSeconds
    });

    if (!vmaValue || !vmaPercentage || vmaValue <= 0 || vmaPercentage <= 0) {
        showNotification('Please enter valid MAS value and percentage', 'warning');
        return;
    }

    // Block calculation if both distance and time are provided
    if (distance && targetTimeSeconds) {
        showNotification('Please choose either distance OR target time, not both', 'danger');
        return;
    }

    // Enhanced validation for distance based on unit
    if (distance) {
        let maxDistance = 1000000; // 1,000,000 meters max
        let minDistance = 100; // 100 meters min
        
        if (distanceUnit === 'km') {
            maxDistance = 1000; // 1000 km max
            minDistance = 0.1; // 100m in km
        } else if (distanceUnit === 'miles') {
            maxDistance = 621; // ~1000km in miles
            minDistance = 0.062; // ~100m in miles
        }
        
        if (distance <= 0 || distance < minDistance || distance > maxDistance) {
            const unitText = distanceUnit === 'm' ? 'meters' : distanceUnit === 'km' ? 'kilometers' : 'miles';
            showNotification(`Please enter a realistic distance (${minDistance} to ${maxDistance} ${unitText})`, 'warning');
            return;
        }
    }

    // Clear any existing results before new calculation
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.innerHTML = '';
    }

    // Perform fresh calculation with current values
    const results = performCalculations(vmaValue, vmaPercentage, distance, distanceUnit, targetTimeSeconds);
    displayResults(results);
    highlightTrainingZones(vmaPercentage);
}

function performCalculations(vmaValue, vmaPercentage, distance, distanceUnit, targetTime) {
    // Ensure fresh calculation each time
    const actualSpeed = vmaValue * (vmaPercentage / 100);
    const actualSpeedMs = actualSpeed / 3.6;

    let results = [];

    // ALWAYS show these two basic results first (recalculated fresh)
    results.push({
        label: 'Running Speed',
        value: `${actualSpeed.toFixed(2)} km/h`,
        description: `${actualSpeedMs.toFixed(2)} m/s`,
        icon: 'tachometer-alt',
        color: 'primary',
        timestamp: Date.now() // Add timestamp to force refresh
    });

    results.push({
        label: 'Pace per km',
        value: formatTime(3600 / actualSpeed),
        description: `${vmaPercentage}% of MAS`,
        icon: 'clock',
        color: 'info',
        timestamp: Date.now()
    });

    // Case 1: Distance provided (no time)
    if (distance && !targetTime) {
        const distanceInKm = convertDistance(distance, distanceUnit, 'km');
        const timeInSeconds = (distanceInKm / actualSpeed) * 3600;
        
        // Format distance display with appropriate unit
        let distanceDisplay = distance.toString();
        if (distanceUnit === 'km' && distance < 1) {
            distanceDisplay = (distance * 1000) + 'm';
        } else {
            distanceDisplay = distance + distanceUnit;
        }
        
        results.push({
            label: `Time for ${distanceDisplay}`,
            value: formatTime(timeInSeconds),
            description: `At ${vmaPercentage}% MAS`,
            icon: 'stopwatch',
            color: 'success',
            timestamp: Date.now()
        });
    }
    
    // Case 2: Target time provided (no distance)
    else if (targetTime && !distance) {
        const possibleDistanceKm = (actualSpeed * targetTime) / 3600;
        const possibleDistanceM = possibleDistanceKm * 1000;
        
        // Display distance in most appropriate unit (km if >= 1km, otherwise meters)
        let distanceDisplay;
        if (possibleDistanceKm >= 1) {
            distanceDisplay = `${possibleDistanceKm.toFixed(2)} km`;
        } else {
            distanceDisplay = `${possibleDistanceM.toFixed(0)} m`;
        }
        
        results.push({
            label: `Distance in ${formatTargetTimeForDisplay()}`,
            value: distanceDisplay,
            description: `At ${vmaPercentage}% MAS`,
            icon: 'route',
            color: 'success',
            timestamp: Date.now()
        });
    }

    // Case 3: Neither distance nor time provided - only show speed and pace (already added above)

    return results;
}

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    const resultsSection = document.getElementById('resultsSection');
    
    // Force clear previous results
    resultsDiv.innerHTML = '';
    
    // Hide results section briefly to show visual refresh
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }

    // Small delay to ensure DOM is cleared before adding new results
    setTimeout(() => {
        results.forEach((result, index) => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item fade-in';
            resultItem.style.animationDelay = `${index * 0.1}s`;
            
            // Add unique key to force re-render
            resultItem.setAttribute('data-timestamp', result.timestamp || Date.now());
            
            resultItem.innerHTML = `
                <div class="result-icon text-${result.color}">
                    <i class="fas fa-${result.icon}"></i>
                </div>
                <div class="result-value text-${result.color}">${result.value}</div>
                <div class="result-label">${result.label}</div>
                <div class="result-description">${result.description}</div>
            `;
            resultsDiv.appendChild(resultItem);
        });

        // Show results section
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        showNotification('Calculation updated successfully', 'success');
    }, 50); // Brief delay to ensure visual refresh
}

function highlightTrainingZones(vmaPercentage) {
    // Reset all zones
    document.querySelectorAll('.training-zone').forEach(zone => {
        zone.style.backgroundColor = '#f8f9fa';
        zone.style.fontWeight = 'normal';
        zone.style.borderLeftWidth = '4px';
    });

    // Highlight current zone
    let currentZone = null;
    if (vmaPercentage >= 70 && vmaPercentage <= 80) currentZone = 'aerobic';
    else if (vmaPercentage >= 80 && vmaPercentage <= 90) currentZone = 'tempo';
    else if (vmaPercentage >= 90 && vmaPercentage <= 95) currentZone = 'vo2max';
    else if (vmaPercentage >= 95 && vmaPercentage <= 105) currentZone = 'neuromuscular';

    if (currentZone) {
        const zoneElement = document.querySelector(`[data-zone="${currentZone}"]`);
        if (zoneElement) {
            zoneElement.style.backgroundColor = '#e3f2fd';
            zoneElement.style.fontWeight = '600';
            zoneElement.style.borderLeftWidth = '6px';
        }
    }
}

function showNotification(message, type = 'info') {
    // Simple notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = `
        top: 20px; right: 20px; z-index: 9999; min-width: 300px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    const iconMap = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas fa-${iconMap[type]} mr-2"></i>
        ${message}
        <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
        </button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 150);
        }
    }, 4000);
}

function loadCalculationHistory() {
    showNotification('History feature - coming soon!', 'info');
}

function exportLastCalculation() {
    showNotification('Export feature - coming soon!', 'info');
}

// Add this new function to handle unit conversion in dropdown
function handleDistanceUnitChange() {
    const distanceInput = document.getElementById('distance');
    const distanceUnit = document.getElementById('distanceUnit');
    
    if (!distanceInput.value) return; // No distance entered, nothing to convert
    
    const currentValue = parseFloat(distanceInput.value);
    const newUnit = distanceUnit.value;
    
    // Get the previously selected unit (stored as data attribute)
    const previousUnit = distanceUnit.dataset.previousUnit || 'm';
    
    if (previousUnit !== newUnit) {
        // Convert the distance
        const convertedValue = convertDistance(currentValue, previousUnit, newUnit);
        distanceInput.value = convertedValue.toFixed(convertedValue < 1 ? 3 : 2);
        
        // Update the visual state of preset buttons with new value
        updateDistancePresetButtons(convertedValue, newUnit);
    }
    
    // Store current unit for next change
    distanceUnit.dataset.previousUnit = newUnit;
}

// Helper function to update distance preset button states
function updateDistancePresetButtons(value, unit) {
    document.querySelectorAll('.distance-presets .preset-btn').forEach(btn => {
        btn.classList.remove('btn-success', 'active');
        btn.classList.add('btn-outline-success');
        
        const btnText = btn.textContent.trim();
        let expectedText = '';
        
        if (unit === 'km' && value < 1) {
            expectedText = (value * 1000) + 'm';
        } else if (unit === 'km') {
            expectedText = value + 'km';
        } else if (unit === 'm') {
            expectedText = value + 'm';
        } else {
            expectedText = value + unit;
        }
        
        if (btnText === expectedText || 
            (btnText === 'Half' && Math.abs(value - 21.1) < 0.1) || 
            (btnText === 'Marathon' && Math.abs(value - 42.2) < 0.1)) {
            btn.classList.remove('btn-outline-success');
            btn.classList.add('btn-success', 'active');
        }
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set default distance unit to meters
    const distanceUnit = document.getElementById('distanceUnit');
    if (distanceUnit) {
        distanceUnit.value = 'm'; // Set default to meters
        distanceUnit.dataset.previousUnit = 'm'; // Set initial previous unit to meters
        distanceUnit.addEventListener('change', handleDistanceUnitChange);
    }
    
    console.log('MAS Calculator loaded successfully with meters as default unit!');
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in forwards;
        opacity: 0;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);