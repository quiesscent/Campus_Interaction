class CommentsManager {
    constructor() {
        this.template = document.getElementById('commentTemplate');
        this.currentPostId = null;
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = false;
        
        // Bind event listeners
        this.bindEvents();
    }
    
    bindEvents() {
        // Listen for comment section open requests
        window.addEventListener('openComments', async (event) => {
            this.currentPostId = event.detail;
            await this.loadComments(true);
        });
    }
    
    async loadComments(reset = false) {
        if (!this.currentPostId) return;
        
        if (reset) {
            this.currentPage = 1;
            this.hasMore = true;
            // Clear existing comments
            const container = document.querySelector(`[data-post-id="${this.currentPostId}"] .comments-container`);
            if (container) container.innerHTML = '';
        }
        
        if (!this.hasMore || this.loading) return;
        
        try {
            this.loading = true;
            const post = await API.getPost(this.currentPostId);
            this.renderComments(post.comments);
        } catch (error) {
            showNotification('Error loading comments', 'error');
        } finally {
            this.loading = false;
        }
    }
    
    createCommentElement(comment) {
        const template = this.template.content.cloneNode(true);
        const commentElement = template.querySelector('.comment');
        
        // Set comment ID
        commentElement.dataset.commentId = comment.id;
        
        // Set user info
        const avatar = commentElement.querySelector('.comment-avatar');
        avatar.src = comment.user.avatar_url || '/static/images/default-avatar.png';
        avatar.alt = `${comment.user.username}'s avatar`;
        
        commentElement.querySelector('.comment-username').textContent = comment.user.username;
        commentElement.querySelector('.comment-content').textContent = comment.content;
        commentElement.querySelector('.comment-date').textContent = this.formatDate(comment.created_at);
        commentElement.querySelector('.comment-likes-count').textContent = comment.likes_count;
        
        // Setup interactions
        this.setupCommentInteractions(commentElement, comment);
        
        return commentElement;
    }
    
    setupCommentInteractions(commentElement, comment) {
        const likeBtn = commentElement.querySelector('.comment-like-btn');
        const deleteBtn = commentElement.querySelector('.comment-delete');
        const reportBtn = commentElement.querySelector('.comment-report');
        const replyBtn = commentElement.querySelector('.comment-reply-btn');
        
        // Like button
        likeBtn.addEventListener('click', async () => {
            try {
                const response = await API.likeComment(comment.id);
                const likesCount = commentElement.querySelector('.comment-likes-count');
                likesCount.textContent = response.likes_count;
                
                const icon = likeBtn.querySelector('i');
                icon.classList.toggle('far');
                icon.classList.toggle('fas');
                icon.classList.toggle('text-danger');
            } catch (error) {
                showNotification('Error liking comment', 'error');
            }
        });
        
        // Delete button (only for comment owner)
        if (comment.is_owner) {
            deleteBtn.addEventListener('click', async () => {
                if (confirm('Are you sure you want to delete this comment?')) {
                    try {
                        await API.deleteComment(comment.id);
                        commentElement.remove();
                        showNotification('Comment deleted successfully', 'success');
                        
                        // Update comment count in post
                        const post = document.querySelector(`[data-post-id="${this.currentPostId}"]`);
                        const countElement = post.querySelector('.post-comments-count');
                        countElement.textContent = parseInt(countElement.textContent) - 1;
                    } catch (error) {
                        showNotification('Error deleting comment', 'error');
                    }
                }
            });
        } else {
            deleteBtn.parentElement.remove();
        }
        
        // Report button
        reportBtn.addEventListener('click', () => {
            window.dispatchEvent(new CustomEvent('openReportModal', {
                detail: {
                    type: 'comment',
                    id: comment.id
                }
            }));
        });
        
        // Reply button
        replyBtn.addEventListener('click', () => {
            const textarea = document.querySelector(`[data-post-id="${this.currentPostId}"] .comment-input`);
            if (textarea) {
                textarea.value = `@${comment.user.username} `;
                textarea.focus();
            }
        });
    }
    
    async addComment(postId, content) {
        try {
            const response = await API.addComment(postId, content);
            const commentElement = this.createCommentElement(response.comment);
            
            // Add to container
            const container = document.querySelector(`[data-post-id="${postId}"] .comments-container`);
            container.insertBefore(commentElement, container.firstChild);
            
            // Update comment count
            const countElement = document.querySelector(`[data-post-id="${postId}"] .post-comments-count`);
            countElement.textContent = parseInt(countElement.textContent) + 1;
            
            return response.comment;
        } catch (error) {
            showNotification('Error adding comment', 'error');
            throw error;
        }
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        // Less than 1 minute
        if (diff < 60000) {
            return 'Just now';
        }
        
        // Less than 1 hour
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes}m ago`;
        }
        
        // Less than 1 day
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}h ago`;
        }
        
        // Less than 1 week
        if (diff < 604800000) {
            const days = Math.floor(diff / 86400000);
            return `${days}d ago`;
        }
        
        // Default to full date
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
}

// Initialize comments manager
const commentsManager = new CommentsManager();

// Export for use in other modules
window.commentsManager = commentsManager;