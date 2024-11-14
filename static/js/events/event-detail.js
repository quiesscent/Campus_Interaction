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
    document.addEventListener('click', async (e) => {
        if (e.target.closest('.reply-button')) {
            const replyButton = e.target.closest('.reply-button');
            const commentId = replyButton.dataset.commentId;
            toggleReplyForm(commentId);
        }

        if (e.target.closest('.delete-comment, .delete-reply')) {
            const deleteButton = e.target.closest('.delete-comment, .delete-reply');
            const commentId = deleteButton.dataset.commentId || deleteButton.dataset.replyId;
            const url = deleteButton.dataset.url;
            if (url && commentId) {
                await deleteComment(commentId, url);
            }
        }

        if (e.target.closest('.toggle-replies')) {
            const toggleButton = e.target.closest('.toggle-replies');
            const commentId = toggleButton.dataset.commentId;
            toggleReplies(commentId);
        }
    });

    const commentForm = document.querySelector('#comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', handleFormSubmit);
    }
}



// Delete comment function with confirmation prompt
async function deleteComment(commentId, url) {
    const confirmation = confirm("Are you sure you want to delete this comment?");
    if (!confirmation) return;
    
    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById(`comment-${commentId}`)?.remove();
            showNotification('Comment deleted successfully!', 'success');
        } else {
            throw new Error(data.message || 'Failed to delete comment');
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Toggle replies display with animation
function toggleReplies(commentId) {
    const repliesContainer = document.getElementById(`replies-${commentId}`);
    const toggleButton = document.querySelector(`[data-comment-id="${commentId}"].toggle-replies`);
    
    if (!repliesContainer || !toggleButton) return;
    
    const isHidden = repliesContainer.style.display === 'none';
    repliesContainer.style.display = isHidden ? 'block' : 'none';
    
    // Update button text and icon
    const replyCount = repliesContainer.children.length;
    toggleButton.innerHTML = `
        <i class="fas fa-chevron-${isHidden ? 'up' : 'down'} me-1"></i>
        ${isHidden ? 'Hide' : 'Show'} ${replyCount} repl${replyCount === 1 ? 'y' : 'ies'}
    `;
}

// Toggle reply form display
function toggleReplyForm(commentId) {
    const replyForm = document.querySelector(`#reply-form-${commentId}`);
    if (replyForm) {
        replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
    }
}


async function handleFormSubmit(e) {
    e.preventDefault(); // Prevent page refresh

    console.log('Form submit event captured, preventDefault() should stop refresh.');

    const form = e.target;

    // Verify form method
    if (form.method.toLowerCase() !== 'post') {
        console.error('Form method is not POST. Please set method="post" in your HTML.');
        return;
    }

    const submitButton = form.querySelector('button[type="submit"]');
    const formData = new FormData(form);

    // Debugging: Log the action and data being sent
    console.log('Form action URL:', form.action);
    console.log('FormData contents:', Object.fromEntries(formData));

    try {
        showLoadingState(submitButton);

        // Confirm that fetch is sending a POST request
        const response = await fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            body: formData
        });

        const data = await response.json();
        console.log('Response status:', response.status);
        console.log('Response data:', data);

        if (!response.ok) throw new Error(data.message || 'Error posting comment');

        if (data.status === 'success') {
            form.reset();
            const parentId = formData.get('parent_comment_id');
            parentId ? handleReplySubmission(parentId, data.comment_html) 
                     : handleMainCommentSubmission(data.comment_html);
            showNotification('Comment posted successfully!', 'success');
        }
    } catch (error) {
        showNotification(error.message, 'error');
        console.error('Error during form submission:', error);
    } finally {
        resetSubmitButton(submitButton);
    }
}



function handleMainCommentSubmission(commentHtml) {
    const commentsContainer = document.getElementById('main-comments');
    const newComment = document.createElement('div');
    newComment.innerHTML = commentHtml.trim();
    commentsContainer.prepend(newComment);
}

function handleReplySubmission(parentId, commentHtml) {
    const repliesContainer = document.getElementById(`replies-${parentId}`);
    const newReply = document.createElement('div');
    newReply.innerHTML = commentHtml.trim();
    repliesContainer.prepend(newReply);
}

// Show loading spinner on submit button
function showLoadingState(button) {
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Posting...';
}

// Reset submit button after submission
function resetSubmitButton(button) {
    button.disabled = false;
    button.innerHTML = '<i class="fas fa-paper-plane"></i> Post';
}

// Main comment and reply handling
function handleMainCommentSubmission(commentHtml) {
    const commentsContainer = document.getElementById('main-comments');
    const newComment = document.createElement('div');
    newComment.innerHTML = commentHtml.trim();
    commentsContainer.prepend(newComment);
}

function handleReplySubmission(parentId, commentHtml) {
    const repliesContainer = document.getElementById(`replies-${parentId}`);
    const newReply = document.createElement('div');
    newReply.innerHTML = commentHtml.trim();
    repliesContainer.prepend(newReply);
}

// Display notifications
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    document.body.prepend(notification);
    setTimeout(() => notification.remove(), 3000);
}

