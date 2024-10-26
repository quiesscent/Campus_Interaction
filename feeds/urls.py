from django.urls import path
from . import views

app_name = "feeds"

urlpatterns = [
    # Basic feed view (HTML rendered view)
    path("feed/", views.home, name="feed"),
    # API endpoints (JSON responses)
    # Feed and posts
    path("api/feed/list/", views.feed, name="api_feed_list"),
    path("api/posts/create/", views.create_post, name="create_post"),
    path("api/posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("api/posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    # Post interactions
    path("api/posts/<int:post_id>/like/", views.like_post, name="like_post"),
    path("api/posts/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path(
        "api/posts/<int:post_id>/view/",
        views.increment_view_count,
        name="increment_view_count",
    ),
    # Engagement analytics
    path(
        "api/posts/<int:post_id>/engagement/<str:engagement_type>/",
        views.post_engagement,
        name="post_engagement",
    ),
    path("api/suggested-users/", views.suggested_users, name="api_suggested_users"),
    # Add these to your urlpatterns
    path(
        "api/comments/<int:comment_id>/like/", views.like_comment, name="like_comment"
    ),
    path(
        "api/comments/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
]
