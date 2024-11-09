// Global constants and state
let currentPage = 1;
let csrfToken;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', initializeApp);

function initializeApp() {
    // Get CSRF token
    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
    csrfToken = csrfTokenMeta ? csrfTokenMeta.content : 
                document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    if (!csrfToken) {
        console.error('CSRF token not found');
        return;
    }

    initializeEventHandlers();
}
function initializeEventHandlers() {
    // Use event delegation for dynamic elements
    document.addEventListener('click', (e) => {
        // Handle reply buttons
        if (e.target.closest('.reply-button')) {
            const commentId = e.target.closest('.reply-button').dataset.commentId;
            toggleReplyForm(commentId);
        }
        
        // Handle like buttons
        if (e.target.closest('.like-button')) {
            const button = e.target.closest('.like-button');
            const commentId = button.dataset.commentId;
            debouncedToggleLike(commentId);
        }
        
        // Handle delete buttons
        if (e.target.closest('.delete-comment-btn')) {
            const button = e.target.closest('.delete-comment-btn');
            const commentId = button.dataset.commentId;
            deleteComment(commentId);
        }
    });

    // Initialize all comment forms
    initializeForms();
}

function initializeForms() {
    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

function initializeDeleteButton() {
    const deleteButton = document.querySelector('.delete-event-btn');
    if (deleteButton) {
        deleteButton.addEventListener('click', async () => {
            const eventId = deleteButton.dataset.eventId;
            if (confirm("Are you sure you want to delete this event? This action cannot be undone.")) {
                await deleteEvent(eventId);
            }
        });
    }
}

// Form handling functions
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    if (form.submitting) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    const formData = new FormData(form);
    const eventId = window.location.pathname.split('/')[2];

    try {
        form.submitting = true;
        showLoadingState(submitButton);

        const response = await fetch(form.action || `/events/${eventId}/comment/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            body: formData
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error posting comment');
        }

        if (data.status === 'success') {
            form.reset();
            const parentId = formData.get('parent_comment_id');

            if (parentId) {
                handleReplySubmission(parentId, data.comment_html);
                updateRepliesCount(parentId, 1);
            } else {
                handleMainCommentSubmission(data.comment_html);
            }

            showNotification('Comment posted successfully!', 'success');
        }
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        resetSubmitButton(submitButton);
        form.submitting = false;
    }
}

// Updated comment handling functions
async function handleSubmissionResponse(data, formData, form) {
    if (data.status === 'success') {
        form.reset();
        const parentId = formData.get('parent_comment_id');
        
        if (parentId) {
            handleReplySubmission(parentId, data.comment_html);
            updateRepliesCount(parentId, 1);
        } else {
            handleMainCommentSubmission(data.comment_html);
        }
        
        showNotification('Comment posted successfully!', 'success');
    }
}

function handleReplySubmission(parentId, commentHtml) {
    const repliesContainer = document.getElementById(`replies-${parentId}`);
    const repliesSection = document.querySelector(`#comment-${parentId} .replies-section`);
    
    if (!repliesSection) {
        // Create new replies section if it doesn't exist
        const newRepliesSection = `
            <div class="replies-section mt-3">
                <button 
                    onclick="toggleReplies(${parentId})" 
                    class="btn btn-sm btn-link text-decoration-none ps-0"
                >
                    <i class="fas fa-chevron-down me-1"></i>
                    Show 1 reply
                </button>
                <div id="replies-${parentId}" class="replies-container mt-2 ms-4" style="display: block;">
                    ${commentHtml}
                </div>
            </div>
        `;
        document.querySelector(`#comment-${parentId} .flex-grow-1`).insertAdjacentHTML('beforeend', newRepliesSection);
    } else {
        if (!repliesContainer) {
            // Create replies container if it doesn't exist
            const container = document.createElement('div');
            container.id = `replies-${parentId}`;
            container.className = 'replies-container mt-2 ms-4';
            repliesSection.appendChild(container);
        }
        repliesContainer.style.display = 'block';
        repliesContainer.insertAdjacentHTML('afterbegin', commentHtml);
    }
    toggleReplyForm(parentId);
}

function updateRepliesCount(commentId, change) {
    const toggleButton = document.querySelector(`#comment-${commentId} .replies-section button`);
    if (toggleButton) {
        const currentCount = parseInt(toggleButton.textContent.match(/\d+/)[0]) + change;
        toggleButton.innerHTML = `
            <i class="fas fa-chevron-down me-1"></i>
            Show ${currentCount} repl${currentCount === 1 ? 'y' : 'ies'}
        `;
    }
}

// Add delete functionality
async function deleteComment(commentId, isReply = false) {
    if (!confirm("Are you sure you want to delete this comment? This action cannot be undone.")) {
        return;
    }

    try {
        const response = await fetch(`/events/comment/${commentId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) throw new Error('Failed to delete comment');

        const elementId = isReply ? `reply-${commentId}` : `comment-${commentId}`;
        const element = document.getElementById(elementId);
        
        if (element) {
            if (isReply) {
                // Update reply count
                const parentId = element.closest('.replies-container').id.split('-')[1];
                updateRepliesCount(parentId, -1);
            }
            element.remove();
            showNotification('Comment deleted successfully', 'success');
        }
    } catch (error) {
        showNotification('Error deleting comment', 'error');
    }
}

async function submitFormData(form, formData, eventId) {
    const response = await fetch(form.action || `/events/${eventId}/comment/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        },
        body: formData
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.message || 'Error posting comment');
    }
    return data;
}

// UI State Management
function showLoadingState(button) {
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Posting...';
}

function resetSubmitButton(button) {
    button.disabled = false;
    button.innerHTML = '<i class="fas fa-paper-plane"></i> Post';
}

// Comment and Reply Functions
async function handleSubmissionResponse(data, formData, form) {
    if (data.status === 'success') {
        form.reset();
        const parentId = formData.get('parent_comment_id');
        
        if (parentId) {
            handleReplySubmission(parentId, data.comment_html);
        } else {
            handleMainCommentSubmission(data.comment_html);
        }
        
        showNotification('Comment posted successfully!', 'success');
    }
}

function handleReplySubmission(parentId, commentHtml) {
    const parentComment = document.getElementById(`comment-${parentId}`);
    if (!parentComment) return;

    let repliesContainer = document.getElementById(`replies-${parentId}`);
    let repliesSection = parentComment.querySelector('.replies-section');

    if (!repliesSection) {
        // Create new replies section
        repliesSection = document.createElement('div');
        repliesSection.className = 'replies-section mt-3';
        repliesSection.innerHTML = `
            <button onclick="toggleReplies(${parentId})" class="btn btn-sm btn-link text-decoration-none ps-0">
                <i class="fas fa-chevron-down me-1"></i> Show 1 reply
            </button>
            <div id="replies-${parentId}" class="replies-container mt-2 ms-4"></div>
        `;
        parentComment.querySelector('.flex-grow-1').appendChild(repliesSection);
        repliesContainer = repliesSection.querySelector('.replies-container');
    }

    // Add new reply with animation
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = commentHtml.trim();
    const newReply = tempDiv.firstElementChild;

    newReply.style.opacity = '0';
    newReply.style.transform = 'translateY(-20px)';
    repliesContainer.insertAdjacentElement('afterbegin', newReply);

    requestAnimationFrame(() => {
        newReply.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        newReply.style.opacity = '1';
        newReply.style.transform = 'translateY(0)';
    });

    // Update reply count and hide form
    updateRepliesCount(parentId, 1);
    toggleReplyForm(parentId);
}

function handleMainCommentSubmission(commentHtml) {
    const commentsContainer = document.getElementById('main-comments');
    const noCommentsMessage = document.querySelector('.no-comments-message');

    if (noCommentsMessage) {
        noCommentsMessage.remove();
    }

    // Parse and animate new comment
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = commentHtml.trim();
    const newComment = tempDiv.firstElementChild;

    // Initialize new comment's forms and buttons
    initializeForms();

    // Animate insertion
    newComment.style.opacity = '0';
    newComment.style.transform = 'translateY(-20px)';
    commentsContainer.insertAdjacentElement('afterbegin', newComment);

    requestAnimationFrame(() => {
        newComment.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        newComment.style.opacity = '1';
        newComment.style.transform = 'translateY(0)';
    });
}


// Toggle Functions
function toggleElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}

function toggleComments() {
    const commentsSection = document.getElementById('main-comments');
    const toggleButton = document.getElementById('toggleCommentsBtn');
    const isHidden = commentsSection.style.display === 'none';
    
    commentsSection.style.display = isHidden ? 'block' : 'none';
    toggleButton.textContent = isHidden ? 'Hide Comments' : 'Show Comments';
}

function toggleReplies(commentId) {
    const repliesContainer = document.getElementById(`replies-${commentId}`);
    const toggleButton = repliesContainer.previousElementSibling;
    const isHidden = repliesContainer.style.display === 'none';
    
    repliesContainer.style.display = isHidden ? 'block' : 'none';
    toggleButton.innerHTML = `
        <i class="fas fa-chevron-${isHidden ? 'up' : 'down'} me-1"></i>
        ${isHidden ? 'Hide' : 'Show'} replies
    `;
}

function toggleReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    if (replyForm) {
        const isHidden = replyForm.style.display === 'none';
        replyForm.style.display = isHidden ? 'block' : 'none';
        if (isHidden) {
            replyForm.querySelector('textarea').focus();
        }
    }
}

// API Functions
async function toggleLike(commentId) {
    try {
        const response = await fetch(`/events/comment/${commentId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) throw new Error('Failed to toggle like');
        
        const data = await response.json();
        updateLikeButton(commentId, data.likes_count);
    } catch (error) {
        showNotification('Error updating like', 'error');
    }
}

async function deleteEvent(eventId) {
    try {
        const response = await fetch(`/events/${eventId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            window.location.href = '/events/';
        } else {
            const data = await response.json();
            showNotification(data.message || "Failed to delete event.", 'error');
        }
    } catch (error) {
        showNotification("Error deleting event.", 'error');
    }
}

async function loadMoreComments(eventId) {
    try {
        currentPage += 1;
        const response = await fetch(`/events/${eventId}/load-more-comments?page=${currentPage}`);
        const data = await response.json();
        
        if (data.comments_html) {
            document.getElementById('comments-container').insertAdjacentHTML('beforeend', data.comments_html);
        } else {
            document.getElementById('load-more-button').style.display = 'none';
        }
    } catch (error) {
        console.error("Error loading comments:", error);
        showNotification('Error loading more comments', 'error');
    }
}

// Helper Functions
function updateLikeButton(commentId, likesCount) {
    const likeButton = document.querySelector(`button[data-comment-id="${commentId}"], button[data-reply-id="${commentId}"]`);
    const likesCountElement = likeButton.querySelector('.likes-count');
    
    likeButton.classList.toggle('btn-danger');
    likeButton.classList.toggle('btn-outline-danger');
    likesCountElement.textContent = likesCount;
}

function handleReplyButtonClick(e) {
    if (e.target.matches('.reply-button')) {
        const commentId = e.target.dataset.commentId;
        toggleReplyForm(commentId);
    }
}

// UI Helper Functions
function showLoadingState(button) {
    if (!button) return;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Posting...';
}

function resetSubmitButton(button) {
    if (!button) return;
    button.disabled = false;
    button.innerHTML = '<i class="fas fa-paper-plane"></i> Post';
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '1050';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Usage example:
const debouncedToggleLike = debounce(toggleLike, 300);
// Make functions available globally
window.toggleReplyForm = toggleReplyForm;
window.toggleReplies = toggleReplies;
window.toggleLike = toggleLike;
window.toggleComments = toggleComments;
window.loadMoreComments = loadMoreComments;