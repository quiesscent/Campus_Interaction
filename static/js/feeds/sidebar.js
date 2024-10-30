// Add new endpoints to API_ENDPOINTS in api.js first
API_ENDPOINTS.SUGGESTED_USERS = '/api/suggested-users/';

// Constants
const DEBOUNCE_DELAY = 300;
const FILTERS = {
    ALL: 'all',
    FOLLOWING: 'following',
    TRENDING: 'trending'
};

// DOM Elements
const searchInput = document.getElementById('searchInput');
const filterButtons = document.querySelectorAll('[data-filter]');
const suggestedUsersContainer = document.getElementById('suggestedUsers');
const suggestedUsersError = document.getElementById('suggestedUsersError');

/**
 * Debounce function to limit API calls
 */
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/**
 * Search functionality
 */
const handleSearch = debounce(async (query) => {
    if (!query.trim()) {
        // Reset feed to default state
        try {
            const data = await API.getFeed(1, 'all');
            // Assuming you have a function to render posts
            renderPosts(data.posts);
        } catch (error) {
            showNotification('Failed to reset feed', 'error');
        }
        return;
    }

    try {
        const data = await API.searchPosts(query);
        // Assuming you have a function to render posts
        renderPosts(data.posts);
    } catch (error) {
        showNotification('Search failed', 'error');
    }
}, DEBOUNCE_DELAY);

/**
 * Filter functionality
 */
function handleFilter(filterType) {
    // Update active state
    filterButtons.forEach(button => {
        button.classList.toggle('active', button.dataset.filter === filterType);
    });

    // Fetch filtered posts
    API.getFeed(1, filterType)
        .then(data => {
            // Assuming you have a function to render posts
            renderPosts(data.posts);
        })
        .catch(error => {
            showNotification('Failed to load filtered posts', 'error');
        });
}

/**
 * Create suggested user card
 */
function createSuggestedUserCard(user) {
    return `
        <div class="d-flex align-items-center mb-3 hover-shadow p-2 rounded-3">
            <img src="${user.avatar_url}" class="rounded-circle me-3"
                alt="${user.username}'s avatar" width="48" height="48"
                style="object-fit: cover;">
            <div class="flex-grow-1">
                <h6 class="mb-1">${user.username}</h6>
                <p class="text-muted small mb-0">${user.course}</p>
            </div>
            <button class="btn btn-primary btn-sm rounded-pill"
                onclick="followUser(${user.id})">
                <i class="fas fa-plus me-1"></i>Follow
            </button>
        </div>
    `;
}

/**
 * Load suggested users
 */
async function loadSuggestedUsers() {
    suggestedUsersError.classList.add('d-none');
    suggestedUsersContainer.innerHTML = `
        <div class="placeholder-glow">
            ${Array(3).fill().map(() => `
                <div class="d-flex align-items-center mb-3">
                    <div class="placeholder rounded-circle me-3" style="width: 48px; height: 48px;"></div>
                    <div class="flex-grow-1">
                        <div class="placeholder col-7 mb-1"></div>
                        <div class="placeholder col-4"></div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    try {
        const response = await apiCall(API_ENDPOINTS.SUGGESTED_USERS);
        if (response.users.length === 0) {
            suggestedUsersContainer.innerHTML = `
                <div class="text-center py-4">
                    <p class="text-muted mb-0">No suggestions available</p>
                </div>
            `;
            return;
        }

        suggestedUsersContainer.innerHTML = response.users
            .map(user => createSuggestedUserCard(user))
            .join('');

    } catch (error) {
        suggestedUsersError.classList.remove('d-none');
        suggestedUsersContainer.innerHTML = '';
    }
}

/**
 * Follow user functionality
 */
async function followUser(userId) {
    try {
        // Assuming you have an endpoint for following users
        // You'll need to add this to your API_ENDPOINTS
        await apiCall(`/api/users/${userId}/follow/`, { method: 'POST' });
        showNotification('Successfully followed user', 'success');
        // Reload suggested users to get new suggestions
        loadSuggestedUsers();
    } catch (error) {
        showNotification('Failed to follow user', 'error');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize search
    searchInput?.addEventListener('input', (e) => handleSearch(e.target.value));

    // Initialize filters
    filterButtons.forEach(button => {
        button.addEventListener('click', () => handleFilter(button.dataset.filter));
    });

    // Load initial suggested users
    loadSuggestedUsers();
});

// Export functions for use in other modules
window.handleFilter = handleFilter;
window.loadSuggestedUsers = loadSuggestedUsers;
window.followUser = followUser;