// Constants
const API_ENDPOINTS = {
    FEED_LIST: '/api/feed/list/',
    CREATE_POST: '/api/posts/create/',
    POST_DETAIL: (postId) => `/api/posts/${postId}/`,
    DELETE_POST: (postId) => `/api/posts/${postId}/delete/`,
    LIKE_POST: (postId) => `/api/posts/${postId}/like/`,
    ADD_COMMENT: (postId) => `/api/posts/${postId}/comment/`,
    VIEW_POST: (postId) => `/api/posts/${postId}/view/`,
    POST_ENGAGEMENT: (postId, type) => `/api/posts/${postId}/engagement/${type}/`,
    SEARCH_POSTS: '/api/posts/search/',
};

// Get CSRF token from cookie
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Base API call function
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        credentials: 'same-origin'
    };

    if (options.method && options.method !== 'GET') {
        if (!(options.body instanceof FormData)) {
            defaultOptions.headers['Content-Type'] = 'application/json';
            if (options.body) options.body = JSON.stringify(options.body);
        }
    }

    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };

    try {
        const response = await fetch(endpoint, finalOptions);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'API call failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Feed API functions
const API = {
    async getFeed(page = 1, filter = 'all') {
        return apiCall(`${API_ENDPOINTS.FEED_LIST}?page=${page}&filter=${filter}`);
    },

    async createPost(formData) {
        return apiCall(API_ENDPOINTS.CREATE_POST, {
            method: 'POST',
            body: formData
        });
    },

    async getPost(postId) {
        return apiCall(API_ENDPOINTS.POST_DETAIL(postId));
    },

    async deletePost(postId) {
        return apiCall(API_ENDPOINTS.DELETE_POST(postId), {
            method: 'POST'
        });
    },

    async likePost(postId) {
        return apiCall(API_ENDPOINTS.LIKE_POST(postId), {
            method: 'POST'
        });
    },

    async addComment(postId, content) {
        return apiCall(API_ENDPOINTS.ADD_COMMENT(postId), {
            method: 'POST',
            body: { content }
        });
    },

    async viewPost(postId) {
        return apiCall(API_ENDPOINTS.VIEW_POST(postId), {
            method: 'POST'
        });
    },

    async getEngagement(postId, type, page = 1) {
        return apiCall(`${API_ENDPOINTS.POST_ENGAGEMENT(postId, type)}?page=${page}`);
    },

    async searchPosts(query, page = 1) {
        return apiCall(`${API_ENDPOINTS.SEARCH_POSTS}?q=${encodeURIComponent(query)}&page=${page}`);
    }
};

// Export API object
window.API = API;