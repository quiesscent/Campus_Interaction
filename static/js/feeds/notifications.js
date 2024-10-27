// Get toast elements
const toastContainer = document.querySelector('.toast-container');
const toastTemplate = document.getElementById('notificationToast');

// Toast types configuration
const TOAST_TYPES = {
    success: {
        icon: 'fas fa-check-circle text-success',
        className: 'border-success'
    },
    error: {
        icon: 'fas fa-times-circle text-danger',
        className: 'border-danger'
    },
    warning: {
        icon: 'fas fa-exclamation-circle text-warning',
        className: 'border-warning'
    },
    info: {
        icon: 'fas fa-info-circle text-info',
        className: 'border-info'
    }
};

/**
 * Show a notification toast
 * @param {string} message - The message to display
 * @param {string} type - Type of notification (success, error, warning, info)
 * @param {string} title - Optional title for the notification
 * @param {number} duration - Optional duration in milliseconds
 */
function showNotification(message, type = 'info', title = '', duration = 3000) {
    // Clone the toast template
    const toast = toastTemplate.cloneNode(true);
    toast.id = `toast-${Date.now()}`;
    
    // Set the type-specific styles
    const typeConfig = TOAST_TYPES[type] || TOAST_TYPES.info;
    const icon = toast.querySelector('.toast-header i');
    icon.className = typeConfig.icon + ' me-2';
    toast.classList.add(typeConfig.className);
    
    // Set content
    const titleElement = toast.querySelector('.toast-title');
    titleElement.textContent = title || type.charAt(0).toUpperCase() + type.slice(1);
    
    const bodyElement = toast.querySelector('.toast-body');
    bodyElement.textContent = message;
    
    // Configure toast options
    toast.setAttribute('data-mdb-delay', duration);
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Initialize MDB toast
    const toastInstance = new mdb.Toast(toast);
    
    // Show the toast
    toastInstance.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.mdb.toast', () => {
        toast.remove();
    });
}

// Export the notification function
window.showNotification = showNotification;