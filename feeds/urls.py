from django.urls import path
from . import views

app_name = "feeds"

urlpatterns = [
    # Basic feed view (HTML rendered view)
    path("feed/", views.home, name="home_feed"),
    # """
    # Landing page with trending posts
    # GET: Returns rendered HTML template with trending posts from last 24 hours
    # Cache: 5 minutes
    # Response template context: {'trending_posts': [...]}
    # """

    # API endpoints (JSON responses)
    path("api/feed/list/", views.feed, name="api_feed_list"),
    # """
    # Main feed endpoint with filtering and pagination
    # GET Parameters:
    #     - page: int (default=1)
    #     - filter: str (options: "all", "following", "trending")
    # Authentication: Required
    # Response: {
    #     "status": "success",
    #     "posts": [{
    #         "id": int,
    #         "content": str,
    #         "user": {"id": int, "username": str},
    #         "created_at": str,
    #         "likes_count": int,
    #         "comments_count": int,
    #         "views_count": int,
    #         "image_url": str|null,
    #         "video_url": str|null,
    #         "recent_comments": [{
    #             "id": int,
    #             "content": str,
    #             "user": {"id": int, "username": str},
    #             "created_at": str
    #         }]
    #     }],
    #     "has_next": bool,
    #     "current_page": int,
    #     "total_pages": int,
    #     "filter_by": str
    # }
    # """

    path("api/posts/create/", views.create_post, name="create_post"),
    # """
    # Create new post with optional media
    # Methods: GET (form), POST (create)
    # Authentication: Required
    # Content-Type: multipart/form-data
    # POST Data:
    #     - content: str
    #     - image: file (optional)
    #     - video: file (optional)
    # Response: {
    #     "status": "success",
    #     "post": {
    #         "id": int,
    #         "content": str,
    #         "user": {"id": int, "username": str},
    #         "created_at": str,
    #         "image_url": str|null,
    #         "video_url": str|null
    #     }
    # }
    # """

    path("api/posts/<int:post_id>/", views.post_detail, name="post_detail"),
    # """
    # Detailed post information including comments
    # GET: Returns complete post data
    # Authentication: Required
    # Response: {
    #     "status": "success",
    #     "post": {
    #         "id": int,
    #         "content": str,
    #         "user": {
    #             "id": int,
    #             "username": str,
    #             "avatar_url": str,
    #             "is_online": bool,
    #             "was_recently_online": bool,
    #             "student_id": str,
    #             "course": str
    #         },
    #         "created_at": str,
    #         "image_url": str|null,
    #         "video_url": str|null,
    #         "likes_count": int,
    #         "views_count": int,
    #         "comments_count": int,
    #         "is_liked": bool,
    #         "is_owner": bool,
    #         "comments": [...]  # Nested comment objects
    #     }
    # }
    # """

    path("api/posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    # """
    # Delete post and associated media
    # POST: Deletes post if user is owner
    # Authentication: Required
    # Authorization: Post owner or staff only
    # Response: {"status": "success"}
    # """

    path("api/posts/<int:post_id>/like/", views.like_post, name="like_post"),
    # """
    # Toggle post like status
    # POST: Toggles like/unlike
    # Authentication: Required
    # Response: {
    #     "status": "success",
    #     "liked": bool,
    #     "likes_count": int
    # }
    # """

    path("api/posts/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    # """
    # Add comment to post
    # POST Data: 
    #     - content: str
    # Authentication: Required
    # Response: {
    #     "status": "success",
    #     "comment": {
    #         "id": int,
    #         "content": str,
    #         "user": {"id": int, "username": str},
    #         "created_at": str,
    #         "likes_count": int
    #     }
    # }
    # """

    path("api/posts/<int:post_id>/view/", views.increment_view_count, name="increment_view_count"),
    # """
    # Increment post view count
    # POST: Records view if not already viewed today
    # Authentication: Required
    # Rate Limit: One view per user per post per day
    # Response: {
    #     "status": "success",
    #     "views_count": int
    # }
    # """

    path("api/posts/<int:post_id>/engagement/<str:engagement_type>/", views.post_engagement, name="post_engagement"),
    # """
    # Get post engagement details
    # GET Parameters:
    #     - engagement_type: str (options: "likes", "comments", "views")
    #     - page: int
    # Authentication: Required
    # Authorization: Post owner or staff only
    # Response: {
    #     "status": "success",
    #     "data": [...],  # Varies by engagement_type
    #     "has_next": bool,
    #     "total_pages": int,
    #     "current_page": int
    # }
    # """

    path("api/suggested-users/", views.suggested_users, name="api_suggested_users"),
    # """
    # Get personalized user suggestions
    # GET: Returns suggested users based on common attributes
    # Authentication: Required
    # Response: {
    #     "users": [{
    #         "id": int,
    #         "username": str,
    #         "avatar_url": str,
    #         "course": str,
    #         "year_of_study": int,
    #         "campus": str,
    #         "mutual_followers": int
    #     }]
    # }
    # """

    path("api/comments/<int:comment_id>/like/", views.like_comment, name="like_comment"),
    # """
    # Like a comment
    # POST: Adds like to comment
    # Authentication: Required
    # Response: {
    #     "message": str,
    #     "likes_count": int
    # }
    # """

    path("api/comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    # """
    # Delete a comment
    # DELETE: Removes comment if user is owner
    # Authentication: Required
    # Authorization: Comment owner only
    # Response: {"message": str}
    # """

    path("api/posts/<int:post_id>/report/", views.report_post, name="report_post"),
    # """
    # Report a post
    # POST Data:
    #     - report_type: str (must be valid Report.REPORT_TYPES)
    #     - description: str (optional)
    # Authentication: Required
    # Response: {
    #     "message": str,
    #     "report_id": int
    # }
    # """

    path("api/comments/<int:comment_id>/report/", views.report_comment, name="report_comment"),
    # """
    # Report a comment
    # POST Data:
    #     - report_type: str (must be valid Report.REPORT_TYPES)
    #     - description: str (optional)
    # Authentication: Required
    # Response: {
    #     "message": str,
    #     "report_id": int
    # }
    # """

    path("api/posts/search/", views.search_posts, name="search_posts"),
    # """
    # Search posts by content, username, or hashtags
    # GET Parameters:
    #     - q: str (search query)
    #     - page: int (default=1)
    # Authentication: Required
    # Response: {
    #     "status": "success",
    #     "posts": [{
    #         "id": int,
    #         "content": str,
    #         "user": {"id": int, "username": str},
    #         "created_at": str,
    #         "likes_count": int,
    #         "comments_count": int,
    #         "views_count": int,
    #         "image_url": str|null,
    #         "video_url": str|null
    #     }],
    #     "has_next": bool,
    #     "current_page": int,
    #     "total_pages": int
    # }
    # """
    
    
]
