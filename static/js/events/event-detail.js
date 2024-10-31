    document.addEventListener('DOMContentLoaded', function () {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Cache selectors
        const mainCommentForm = document.querySelector('form[action*="add_comment"]');
        const deleteButton = document.querySelector('.delete-event-btn');

        // Event handlers for main comment form submission
        if (mainCommentForm) {
            mainCommentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                submitComment(this, mainCommentForm);
            });
        }

        // Event handlers for reply form submissions
        document.querySelectorAll('.reply-form form').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                submitComment(this, form);
            });
        });

        // Delete event handler
        if (deleteButton) {
            deleteButton.addEventListener('click', async () => {
                const eventId = deleteButton.dataset.eventId;
                if (confirm("Are you sure you want to delete this event? This action cannot be undone.")) {
                    await deleteEvent(eventId, csrfToken);
                }
            });
        }
    });

    function toggleElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = element.style.display === 'none' ? 'block' : 'none';
        }
    }

    function toggleComments() {
        toggleElement("main-comments");
    }

    function toggleReplies(commentId) {
        toggleElement(`replies-${commentId}`);
        const repliesDiv = document.getElementById(`replies-${commentId}`);
        const toggleButton = repliesDiv.previousElementSibling;
        const isHidden = repliesDiv.style.display === 'none';
        toggleButton.innerHTML = `
            <i class="fas fa-chevron-${isHidden ? 'up' : 'down'}"></i>
            ${isHidden ? 'Hide' : 'Show'} replies
        `;
    }

    function toggleReplyForm(commentId) {
        toggleElement(`reply-form-${commentId}`);
    }

    async function toggleLike(commentId) {
        try {
            const response = await fetch(`/events/comment/${commentId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                }
            });
            const data = await response.json();
            if (response.ok) {
                const likeButton = document.querySelector(`button[onclick="toggleLike(${commentId})"]`);
                const likeCount = likeButton.querySelector('span');

                // Toggle button appearance
                likeButton.classList.toggle('btn-danger');
                likeButton.classList.toggle('btn-outline-danger');

                // Update like count
                likeCount.textContent = data.likes_count;
            }
        } catch (error) {
            showNotification('Error updating like', 'error');
        }
    }

    async function deleteEvent(eventId, csrfToken) {
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
                alert(data.message || "Failed to delete event.");
            }
        } catch (error) {
            alert("Error deleting event.");
        }
    }

    function submitComment(form, originalForm) {
        const formData = new FormData(form);
        const isReply = formData.get('parent_comment_id') !== null;
        const mainCommentsContainer = document.getElementById('main-comments');
        const submitButton = form.querySelector('button[type="submit"]');

        // Add loading spinner to form submit button
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border spinner-border-sm ms-2';
        submitButton.appendChild(spinner);
        submitButton.disabled = true;  // Disable button to prevent multiple submissions

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken,
            },
            credentials: 'same-origin',
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    handleCommentSubmission(data, isReply, formData, mainCommentsContainer);
                } else {
                    showNotification(data.errors || 'Error posting comment', 'error');
                }
            })
            .catch(() => showNotification('Error posting comment', 'error'))
            .finally(() => {
                spinner.remove();
                submitButton.disabled = false;
            });
    }

    function handleCommentSubmission(data, isReply, formData, mainCommentsContainer) {
        if (isReply) {
            const parentId = formData.get('parent_comment_id');
            const repliesContainer = document.getElementById(`replies-${parentId}`);

            if (repliesContainer) {
                repliesContainer.innerHTML = data.comment_html + repliesContainer.innerHTML;
            } else {
                const parentComment = document.getElementById(`comment-${parentId}`);
                const repliesSection = document.createElement('div');
                repliesSection.className = 'replies-section mt-3 ms-4';
                repliesSection.innerHTML = `
                    <a href="javascript:void(0);" onclick="toggleReplies(${parentId})" class="text-primary mb-2 d-block">
                        <i class="fas fa-chevron-down"></i> Show 1 reply
                    </a>
                    <div id="replies-${parentId}" style="display: none;">
                        ${data.comment_html}
                    </div>
                `;
                parentComment.querySelector('.flex-grow-1').appendChild(repliesSection);
            }

            toggleReplyForm(parentId);
        } else {
            mainCommentsContainer.insertAdjacentHTML('afterbegin', data.comment_html);
            // Remove empty state if it exists
            const emptyState = mainCommentsContainer.querySelector('.text-center.text-muted');
            if (emptyState) {
                emptyState.remove();
            }
        }

        form.reset();
        showNotification('Comment posted successfully!', 'success');
    }

    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '1050';
        notification.textContent = message;

        document.body.appendChild(notification);
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    let currentPage = 1;

    function loadMoreComments(eventId) {
        currentPage += 1;
        $.ajax({
            url: `/events/${eventId}/load-more-comments?page=${currentPage}`,
            type: 'GET',
            success: function(response) {
                if (response.comments_html) {
                    $('#comments-container').append(response.comments_html);
                } else {
                    $('#load-more-button').hide();
                }
            },
            error: function(xhr) {
                console.error("Error loading comments:", xhr);
            }
        });
    }

    function addComment(eventId) {
        const content = $('#comment-input').val();
        const parentCommentId = $('#parent-comment-id').val();
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        $.ajax({
            url: `/events/${eventId}/comment/`,
            type: 'POST',
            data: {
                content: content,
                parent_comment_id: parentCommentId,
                csrfmiddlewaretoken: csrfToken
            },
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                $('#comments-container').append(response.comment_html);
                $('#comment-input').val(''); // Clear the input
                $('#parent-comment-id').val(''); // Clear the parent comment ID
            },
            error: function(xhr) {
                console.error("Error adding comment:", xhr);
            }
        });
    }
// Updated JavaScript for handling comments
document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Handle main comment form submission
    const mainCommentForm = document.getElementById('commentForm');
    if (mainCommentForm) {
        mainCommentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleCommentSubmit(this);
        });
    }

    // Function to handle comment submission
    async function handleCommentSubmit(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        const formData = new FormData(form);
        const eventId = window.location.pathname.split('/')[2]; // Get event ID from URL

        try {
            // Disable submit button and show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Posting...';

            const response = await fetch(`/events/${eventId}/comment/`, {
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
                // Clear form
                form.reset();

                // Handle the response
                const parentId = formData.get('parent_comment_id');
                if (parentId) {
                    // Handle reply
                    const repliesContainer = document.getElementById(`replies-${parentId}`);
                    if (repliesContainer) {
                        repliesContainer.insertAdjacentHTML('afterbegin', data.comment_html);
                        toggleReplyForm(parentId); // Hide reply form after successful submission
                    }
                } else {
                    // Handle main comment
                    const commentsContainer = document.getElementById('main-comments');
                    commentsContainer.insertAdjacentHTML('afterbegin', data.comment_html);
                }

                showNotification('Comment posted successfully!', 'success');
            } else {
                throw new Error(data.message || 'Error posting comment');
            }
        } catch (error) {
            showNotification(error.message, 'error');
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.innerHTML = 'Post Comment';
        }
    }

    // Function to show notifications
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '1050';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Handle reply forms
    document.addEventListener('click', function(e) {
        if (e.target.matches('.reply-button')) {
            const commentId = e.target.dataset.commentId;
            toggleReplyForm(commentId);
        }
    });

    // Initialize reply forms
    document.querySelectorAll('.reply-form form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleCommentSubmit(this);
        });
    });
});

// Function to toggle reply form visibility
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

// Function to toggle replies visibility
function toggleReplies(commentId) {
    const repliesContainer = document.getElementById(`replies-${commentId}`);
    const toggleButton = document.querySelector(`button[onclick="toggleReplies(${commentId})"]`);
    if (repliesContainer && toggleButton) {
        const isHidden = repliesContainer.style.display === 'none';
        repliesContainer.style.display = isHidden ? 'block' : 'none';
        toggleButton.innerHTML = isHidden ? 'Hide replies' : 'Show replies';
    }
}
// Comment and Reply Functionality
document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Initialize all forms
    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });

    // Handle form submissions
    async function handleFormSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const formData = new FormData(form);

        try {
            // Show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Posting...';

            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                // Handle successful submission
                form.reset();
                
                if (formData.get('parent_comment_id')) {
                    // Handle reply
                    const parentId = formData.get('parent_comment_id');
                    const repliesContainer = document.getElementById(`replies-${parentId}`);
                    
                    if (repliesContainer) {
                        repliesContainer.style.display = 'block';
                        repliesContainer.insertAdjacentHTML('afterbegin', data.comment_html);
                    }
                    
                    toggleReplyForm(parentId);
                } else {
                    // Handle main comment
                    const commentsContainer = document.getElementById('main-comments');
                    commentsContainer.insertAdjacentHTML('afterbegin', data.comment_html);
                }

                showNotification('Comment posted successfully!', 'success');
            } else {
                throw new Error(data.message || 'Error posting comment');
            }
        } catch (error) {
            showNotification(error.message, 'error');
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Post';
        }
    }

    // Like functionality
    async function toggleLike(id) {
        try {
            const response = await fetch(`/events/comment/${id}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) throw new Error('Failed to toggle like');

            const data = await response.json();
            
            // Update like button
            const likeButton = document.querySelector(`button[data-comment-id="${id}"], button[data-reply-id="${id}"]`);
            const likesCount = likeButton.querySelector('.likes-count');
            
            likeButton.classList.toggle('btn-danger');
            likeButton.classList.toggle('btn-outline-danger');
            likesCount.textContent = data.likes_count;
            
        } catch (error) {
            showNotification('Error updating like', 'error');
        }
    }

    // Helper functions
    window.toggleReplyForm = function(commentId) {
        const replyForm = document.getElementById(`reply-form-${commentId}`);
        const isHidden = replyForm.style.display === 'none';
        
        replyForm.style.display = isHidden ? 'block' : 'none';
        
        if (isHidden) {
            replyForm.querySelector('textarea').focus();
        }
    };

    window.toggleReplies = function(commentId) {
        const repliesContainer = document.getElementById(`replies-${commentId}`);
        const toggleButton = repliesContainer.previousElementSibling;
        const isHidden = repliesContainer.style.display === 'none';
        
        repliesContainer.style.display = isHidden ? 'block' : 'none';
        toggleButton.innerHTML = `
            <i class="fas fa-chevron-${isHidden ? 'up' : 'down'} me-1"></i>
            ${isHidden ? 'Hide' : 'Show'} replies
        `;
    };

    window.toggleLike = toggleLike;
});

// Notification helper
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '1050';
    notification.textContent = message;

    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
