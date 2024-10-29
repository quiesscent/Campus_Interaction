// State management
const PostsState = {
    currentPage: 1,
    currentFilter: 'all',
    loading: false,
    hasMore: true
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
        PostsState.currentPage = 1;
        PostsState.hasMore = true;
        postsContainer.innerHTML = '';
    }

    if (!PostsState.hasMore || PostsState.loading) return;

    try {
        PostsState.loading = true;
        showLoading();

        const data = await API.getFeed(PostsState.currentPage, filter);
        
        if (data.posts.length === 0) {
            PostsState.hasMore = false;
            hideLoading();
            return;
        }

        renderPosts(data.posts);
        PostsState.currentPage = data.current_page + 1;
        PostsState.hasMore = data.has_next;
        hideError();
    } catch (error) {
        showError();
    } finally {
        PostsState.loading = false;
        hideLoading();
        updateLoadMoreButton();
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

// Setup post interactions
function setupPostInteractions(postCard, post) {
    const likeBtn = postCard.querySelector('.post-like-btn');
    const commentBtn = postCard.querySelector('.post-comment-btn');
    const shareBtn = postCard.querySelector('.post-share-btn');
    const deleteBtn = postCard.querySelector('.post-delete');
    const engagementBtns = postCard.querySelectorAll('.view-engagement');
    
    // Like button
    likeBtn.addEventListener('click', async () => {
        try {
            const response = await API.likePost(post.id);
            const likesCount = postCard.querySelector('.post-likes-count');
            likesCount.textContent = response.likes_count;
            
            const icon = likeBtn.querySelector('i');
            icon.classList.toggle('far');
            icon.classList.toggle('fas');
            icon.classList.toggle('text-danger');
        } catch (error) {
            showNotification('Error liking post', 'error');
        }
    });
    
    // Comment button
    commentBtn.addEventListener('click', () => {
        // This will be handled by comments.js
        window.dispatchEvent(new CustomEvent('openComments', { detail: post.id }));
    });
    
    // Share button
    shareBtn.addEventListener('click', () => {
        // This will be handled by sharing.js
        window.dispatchEvent(new CustomEvent('sharePost', { detail: post }));
    });
    
    // Delete button (only shown to post owner)
    if (post.is_owner) {
        deleteBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete this post?')) {
                try {
                    await API.deletePost(post.id);
                    postCard.remove();
                    showNotification('Post deleted successfully', 'success');
                } catch (error) {
                    showNotification('Error deleting post', 'error');
                }
            }
        });
    } else {
        deleteBtn.parentElement.remove();
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

    // // Dropdown menu
    // const dropdownBtn = postCard.querySelector('.post-dropdown-btn');
    // const dropdownMenu = postCard.querySelector('.post-dropdown-menu');

    // if (dropdownBtn && dropdownMenu) {
    //     new Popper.createPopper(dropdownBtn, dropdownMenu, {
    //         placement: 'bottom-end',
    //         modifiers: [
    //             {
    //                 name: 'offset',
    //                 options: {
    //                     offset: [0, 8],
    //                 },
    //             },
    //         ],
    //     });

    //     dropdownBtn.addEventListener('click', () => {
    //         dropdownMenu.classList.toggle('show');
    //     });

    //     document.addEventListener('click', (e) => {
    //         if (!e.target.closest('.post-dropdown-btn') && !e.target.closest('.post-dropdown-menu')) {
    //             dropdownMenu.classList.remove('show');
    //         }
    //     });
    // }

    
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