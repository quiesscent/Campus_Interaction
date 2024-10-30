// State management
const PostsState = {
    currentPage: 1,
    currentFilter: 'all',
    loading: false,
    hasMore: true,
    searchQuery: '',
    posts: new Map(), // Track loaded posts
    
    reset() {
        this.currentPage = 1;
        this.hasMore = true;
        this.posts.clear();
    },
    
    addPosts(newPosts) {
        newPosts.forEach(post => {
            this.posts.set(post.id, post);
        });
    }
};

// DOM Elements
const postTemplate = document.getElementById('postTemplate');
const postsContainer = document.getElementById('postsContainer');
const loadMoreBtn = document.getElementById('loadMoreBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const postsError = document.getElementById('postsError');



// Initialize infinite scroll
function initInfiniteScroll() {
    const options = {
        root: null,
        rootMargin: '100px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !PostsState.loading && PostsState.hasMore) {
                loadMorePosts();
            }
        });
    }, options);

    if (loadMoreBtn) observer.observe(loadMoreBtn);
}

// Load initial posts
async function loadPosts(filter = 'all', reset = false) {
    if (reset) {
        PostsState.reset();
        postsContainer.innerHTML = '';
    }

    if (!PostsState.hasMore || PostsState.loading) return;

    try {
        PostsState.loading = true;
        showLoading();

        const endpoint = PostsState.searchQuery
            ? `${API_ENDPOINTS.SEARCH_POSTS}?q=${encodeURIComponent(PostsState.searchQuery)}&page=${PostsState.currentPage}`
            : `${API_ENDPOINTS.FEED_LIST}?page=${PostsState.currentPage}&filter=${filter}`;

        const data = await apiCall(endpoint);
        
        if (data.posts?.length === 0) {
            PostsState.hasMore = false;
            if (reset && !PostsState.posts.size) {
                showEmptyState();
            }
            return;
        }

        PostsState.addPosts(data.posts);
        renderPosts(data.posts);
        PostsState.currentPage = data.current_page + 1;
        PostsState.hasMore = data.has_next;
        hideError();
    } catch (error) {
        handleLoadError(error);
    } finally {
        PostsState.loading = false;
        hideLoading();
        updateLoadMoreButton();
    }
}

function handleLoadError(error) {
    console.error('Load error:', error);
    
    const errorMessage = error.status === 429 
        ? 'Too many requests. Please wait a moment.'
        : 'Error loading posts. Please try again.';
    
    showError(errorMessage);
    
    if (error.status === 401) {
        // Handle unauthorized access
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
    }
}

// Render posts
function renderPosts(posts) {
    posts.forEach(post => {
        const postElement = createPostElement(post);
        postsContainer.appendChild(postElement);
        
        // Record view after rendering using debounced version
        viewPostDebounced(post.id);
    });
}

// Create post element from template
function createPostElement(post) {
    console.log('Post owner status:', post.is_owner);
    const template = postTemplate.content.cloneNode(true);
    const postCard = template.querySelector('.post-card');
    postCard.dataset.postId = post.id;
    
    // Set post ID
    postCard.dataset.postId = post.id;
    
    // Set user info
    const avatar = postCard.querySelector('.post-avatar');
    avatar.src = post.user.avatar_url || '/static/images/default-avatar.png';
    avatar.alt = `${post.user.username}'s avatar`;
    
    postCard.querySelector('.post-username').textContent = post.user.username;
    postCard.querySelector('.post-date').textContent = formatDate(post.created_at);
    
    // Set course and campus if available
    const courseElement = postCard.querySelector('.user-course');
    const campusElement = postCard.querySelector('.user-campus');
    
    if (post.user.course) {
        courseElement.textContent = post.user.course;
        courseElement.classList.remove('d-none');
    }
    
    if (post.user.campus) {
        campusElement.textContent = post.user.campus;
        campusElement.classList.remove('d-none');
    }
    
    // Set post content
    const contentElement = postCard.querySelector('.post-content');
    contentElement.innerHTML = formatContent(post.content);
    
    // Add media if present
    if (post.image_url) {
        const img = document.createElement('img');
        img.src = post.image_url;
        img.className = 'img-fluid rounded mb-3';
        img.alt = 'Post image';
        contentElement.appendChild(img);
    } else if (post.video_url) {
        const video = document.createElement('video');
        video.src = post.video_url;
        video.className = 'w-100 rounded mb-3';
        video.controls = true;
        contentElement.appendChild(video);
    }
    
    // Set counts
    postCard.querySelector('.post-likes-count').textContent = post.likes_count;
    postCard.querySelector('.post-comments-count').textContent = post.comments_count;
    postCard.querySelector('.post-views-count').textContent = post.views_count;
    
    // Add event listeners
    setupPostInteractions(postCard, post);
    
    return postCard;
}

// In posts.js, update the setupPostInteractions function:

function setupPostInteractions(postCard, post) {
    const likeBtn = postCard.querySelector('.post-like-btn');
    const commentBtn = postCard.querySelector('.post-comment-btn');
    const shareBtn = postCard.querySelector('.post-share-btn');
    const ownerActions = postCard.querySelector('.post-owner-actions');
    const nonOwnerActions = postCard.querySelector('.post-non-owner-actions');
    const deleteBtn = postCard.querySelector('.post-delete');
    const reportBtn = postCard.querySelector('.post-report');
    const engagementBtns = postCard.querySelectorAll('.view-engagement');
    
    // Set up visibility based on ownership
    if (post.is_owner) {
        ownerActions?.classList.remove('d-none');
        nonOwnerActions?.classList.add('d-none');
    } else {
        ownerActions?.classList.add('d-none');
        nonOwnerActions?.classList.remove('d-none');
    }

    // Like button handler using handlePostInteraction
    if (likeBtn) {
        likeBtn.addEventListener('click', async () => {
            const likesCount = postCard.querySelector('.post-likes-count');
            const icon = likeBtn.querySelector('i');
            
            await handlePostInteraction(
                post.id,
                () => API.likePost(post.id),
                (response) => {
                    likesCount.textContent = response.likes_count;
                    icon.classList.toggle('far');
                    icon.classList.toggle('fas');
                    icon.classList.toggle('text-danger');
                }
            );
        });
    }

    // Delete button handler using handlePostInteraction
    if (deleteBtn && post.is_owner) {
        deleteBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete this post?')) {
                await handlePostInteraction(
                    post.id,
                    () => API.deletePost(post.id),
                    () => {
                        postCard.remove();
                        showNotification('Post deleted successfully', 'success');
                    }
                );
            }
        });
    }

    // Report button handler using handlePostInteraction
    if (reportBtn && !post.is_owner) {
        reportBtn.addEventListener('click', async () => {
            if (window.reportModal) {
                window.reportModal.setupReport(post.id, 'post');
                const reportModalElement = document.getElementById('reportModal');
                const modal = new mdb.Modal(reportModalElement);
                modal.show();
            }
        });
    }

    // Comment button (opens modal/section)
    if (commentBtn) {
        commentBtn.addEventListener('click', () => {
            window.dispatchEvent(new CustomEvent('openComments', { 
                detail: post.id 
            }));
        });
    }
    
    // Share button (opens modal)
    if (shareBtn) {
        shareBtn.addEventListener('click', () => {
            window.dispatchEvent(new CustomEvent('sharePost', { 
                detail: post 
            }));
        });
    }
    
    // Engagement buttons
    engagementBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.dataset.type;
            window.dispatchEvent(new CustomEvent('viewEngagement', { 
                detail: { postId: post.id, type }
            }));
        });
    });
}

// Add this helper function to handle post interactions
async function handlePostInteraction(postId, action, updateUI) {
    try {
        const response = await action();
        updateUI(response);
    } catch (error) {
        if (error.status === 401) {
            showNotification('Please log in to perform this action', 'error');
        } else if (error.status === 403) {
            showNotification('You do not have permission to perform this action', 'error');
        } else if (error.status === 404) {
            showNotification('This post is no longer available', 'error');
            // Optionally remove the post from view
            const postElement = document.querySelector(`[data-post-id="${postId}"]`);
            postElement?.remove();
        } else {
            showNotification('Error performing action', 'error');
        }
        throw error;
    }
}

// Helper functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatContent(content) {
    // Convert URLs to links
    content = content.replace(
        /(https?:\/\/[^\s]+)/g,
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    // Convert hashtags to links
    content = content.replace(
        /#(\w+)/g,
        '<a href="/search?q=%23$1">#$1</a>'
    );
    
    // Convert mentions to links
    content = content.replace(
        /@(\w+)/g,
        '<a href="/profile/$1">@$1</a>'
    );
    
    return content;
}

function showLoading() {
    loadingSpinner.classList.remove('d-none');
    loadMoreBtn.classList.add('d-none');
}

function hideLoading() {
    loadingSpinner.classList.add('d-none');
    updateLoadMoreButton();
}

function showError() {
    postsError.classList.remove('d-none');
}

function hideError() {
    postsError.classList.add('d-none');
}

function updateLoadMoreButton() {
    if (PostsState.hasMore) {
        loadMoreBtn.classList.remove('d-none');
    } else {
        loadMoreBtn.classList.add('d-none');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPosts();
    initInfiniteScroll();
    
    // Listen for filter changes
    window.addEventListener('changeFilter', (event) => {
        PostsState.currentFilter = event.detail;
        loadPosts(event.detail, true);
    });
});