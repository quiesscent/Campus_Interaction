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
    // Use event delegation for all button clicks
    document.addEventListener('click', async (e) => {
        // Handle reply buttons
        if (e.target.closest('.reply-button')) {
            const replyButton = e.target.closest('.reply-button');
            const commentId = replyButton.dataset.commentId;
            toggleReplyForm(commentId);
        }
        
        // Handle delete buttons
        if (e.target.closest('.delete-comment, .delete-reply')) {
            const deleteButton = e.target.closest('.delete-comment, .delete-reply');
            const commentId = deleteButton.dataset.commentId || deleteButton.dataset.replyId;
            const url = deleteButton.dataset.url;
            if (url && commentId) {
                await deleteComment(commentId, url);
            }
        }
        
        // Handle toggle replies buttons
        if (e.target.closest('.toggle-replies')) {
            const toggleButton = e.target.closest('.toggle-replies');
            const commentId = toggleButton.dataset.commentId;
            toggleReplies(commentId);
        }
    });

    // Initialize all reply forms with submit handler
    document.querySelectorAll('.reply-form').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}


// Updated toggle replies function
function toggleReplies(commentId) {
    const repliesContainer = document.getElementById(`replies-${commentId}`);
    const toggleButton = document.querySelector(`[data-comment-id="${commentId}"].toggle-replies`);
    
    if (!repliesContainer || !toggleButton) return;
    
    const isHidden = repliesContainer.style.display === 'none';
    
    // Add slide animation
    repliesContainer.style.transition = 'max-height 0.3s ease';
    repliesContainer.style.overflow = 'hidden';
    
    if (isHidden) {
        repliesContainer.style.display = 'block';
        const height = repliesContainer.scrollHeight;
        repliesContainer.style.maxHeight = '0px';
        setTimeout(() => {
            repliesContainer.style.maxHeight = height + 'px';
        }, 0);
    } else {
        repliesContainer.style.maxHeight = '0px';
        setTimeout(() => {
            repliesContainer.style.display = 'none';
        }, 300);
    }
    
    // Update button text and icon
    const replyCount = repliesContainer.children.length;
    toggleButton.innerHTML = `
        <i class="fas fa-chevron-${isHidden ? 'up' : 'down'} me-1"></i>
        ${isHidden ? 'Hide' : 'Show'} ${replyCount} repl${replyCount === 1 ? 'y' : 'ies'}
    `;
}

// Call initialization on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initializeEventHandlers();
});
// Form handling functions

// Updated form submit handler
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    if (form.submitting) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    const formData = new FormData(form);
    
    try {
        form.submitting = true;
        showLoadingState(submitButton);

        const response = await fetch(form.action, {
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

// Updated reply form handling
function handleReplySubmission(parentId, commentHtml) {
    const parentComment = document.getElementById(`comment-${parentId}`);
    if (!parentComment) return;

    let repliesContainer = document.getElementById(`replies-${parentId}`);
    let repliesSection = parentComment.querySelector('.replies-section');

    if (!repliesSection) {
        // Create new replies section if it doesn't exist
        repliesSection = document.createElement('div');
        repliesSection.className = 'replies-section mt-3';
        repliesSection.innerHTML = `
            <button 
                class="btn btn-sm btn-link text-decoration-none ps-0 toggle-replies"
                data-comment-id="${parentId}"
            >
                <i class="fas fa-chevron-down me-1"></i>
                Show 1 reply
            </button>
            <div id="replies-${parentId}" class="replies-container mt-2 ms-4" style="display: block;">
                ${commentHtml}
            </div>
        `;
        parentComment.querySelector('.flex-grow-1').appendChild(repliesSection);
    } else {
        if (!repliesContainer) {
            repliesContainer = document.createElement('div');
            repliesContainer.id = `replies-${parentId}`;
            repliesContainer.className = 'replies-container mt-2 ms-4';
            repliesSection.appendChild(repliesContainer);
        }
        repliesContainer.style.display = 'block';
        repliesContainer.insertAdjacentHTML('afterbegin', commentHtml);
    }

    // Hide reply form after submission
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



// Toggle reply form function
function toggleReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    if (!replyForm) return;

    const isHidden = replyForm.style.display === 'none' || replyForm.style.display === '';
    
    // Hide all other reply forms first
    document.querySelectorAll('.reply-form').forEach(form => {
        if (form.id !== `reply-form-${commentId}`) {
            form.style.display = 'none';
        }
    });

    // Toggle current form with animation
    replyForm.style.transition = 'opacity 0.3s ease';
    if (isHidden) {
        replyForm.style.display = 'block';
        replyForm.style.opacity = '0';
        setTimeout(() => {
            replyForm.style.opacity = '1';
            replyForm.querySelector('textarea')?.focus();
        }, 0);
    } else {
        replyForm.style.opacity = '0';
        setTimeout(() => {
            replyForm.style.display = 'none';
        }, 300);
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



function handleReplyButtonClick(e) {
    if (e.target.matches('.reply-button')) {
        const commentId = e.target.dataset.commentId;
        toggleReplyForm(commentId);
    }
}

// Reply form visibility state
let activeReplyForm = null;

// Toggle reply form visibility

// Updated toggle reply form function
function toggleReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    if (!replyForm) return;

    const isHidden = replyForm.style.display === 'none' || replyForm.style.display === '';
    
    // Hide all other reply forms first
    document.querySelectorAll('.reply-form').forEach(form => {
        if (form.id !== `reply-form-${commentId}`) {
            form.style.display = 'none';
        }
    });

    // Toggle current form with animation
    replyForm.style.transition = 'opacity 0.3s ease';
    if (isHidden) {
        replyForm.style.display = 'block';
        replyForm.style.opacity = '0';
        setTimeout(() => {
            replyForm.style.opacity = '1';
            replyForm.querySelector('textarea')?.focus();
        }, 0);
    } else {
        replyForm.style.opacity = '0';
        setTimeout(() => {
            replyForm.style.display = 'none';
        }, 300);
    }
}
// Helper function to update replies count
function updateRepliesCount(commentId, change) {
    const toggleButton = document.querySelector(`[data-comment-id="${commentId}"].toggle-replies`);
    if (toggleButton) {
        const currentCount = parseInt(toggleButton.textContent.match(/\d+/)[0]) + change;
        toggleButton.innerHTML = `
            <i class="fas fa-chevron-${toggleButton.querySelector('.fa-chevron-down') ? 'down' : 'up'} me-1"></i>
            Show ${currentCount} repl${currentCount === 1 ? 'y' : 'ies'}
        `;
    }
}

// Event delegation handler
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (e) => {
        const replyButton = e.target.closest('.reply-button');
        if (replyButton) {
            const commentId = replyButton.dataset.commentId;
            if (commentId) {
                toggleReplyForm(commentId);
            } else {
                console.error('No comment ID found on reply button');
            }
        }
    });
});

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


// Updated delete comment function with DELETE method
async function deleteComment(commentId, url) {
    if (!confirm("Are you sure you want to delete this comment? This action cannot be undone.")) {
        return;
    }

    try {
        const response = await fetch(url, {
            method: 'DELETE',  // Changed from POST to DELETE
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete comment');
        }

        const data = await response.json();
        
        if (data.status === 'success') {
            const element = document.getElementById(`comment-${commentId}`) || 
                          document.getElementById(`reply-${commentId}`);
            
            if (element) {
                // Add fade-out animation
                element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                element.style.opacity = '0';
                element.style.transform = 'translateY(-20px)';
                
                // Remove element after animation
                setTimeout(() => {
                    if (element.classList.contains('reply-card')) {
                        const parentId = element.closest('.replies-container').id.split('-')[1];
                        updateRepliesCount(parentId, -1);
                    }
                    element.remove();
                }, 300);
                
                showNotification('Comment deleted successfully', 'success');
            }
        }
    } catch (error) {
        showNotification(error.message || 'Error deleting comment', 'error');
        console.error('Delete error:', error);
    }
}


// Make functions available globally
window.toggleReplyForm = toggleReplyForm;
window.toggleReplies = toggleReplies;
window.toggleLike = toggleLike;
window.toggleComments = toggleComments;
window.loadMoreComments = loadMoreComments;