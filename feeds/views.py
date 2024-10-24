# views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.core.paginator import Paginator
from django.db.models import F, Q, Prefetch
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db import transaction
from .models import Post, Comment, PostView, Report, PostLike
from .forms import PostForm, CommentForm
import logging

logger = logging.getLogger(__name__)

POSTS_PER_PAGE = 20
CACHE_TTL = 300  # 5 minutes

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

@cache_page(CACHE_TTL)
def home(request):
    """Landing page with cached response"""
    trending_posts = cache.get_or_set(
        'trending_posts',
        Post.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=1)
        ).order_by('-views_count')[:5],
        CACHE_TTL
    )
    return render(request, "social/home.html", {"trending_posts": trending_posts})

@login_required
def feed(request):
    """Main feed view with pagination and filters"""
    # Get query parameters
    page = request.GET.get('page', 1)
    filter_by = request.GET.get('filter', 'all')
    
    # Base queryset with optimal joins
    posts = Post.objects.select_related('user').prefetch_related(
        Prefetch('comments', queryset=Comment.objects.select_related('user').order_by('-created_at')[:3]),
        'likes'
    ).filter(status='published')

    # Apply filters
    if filter_by == 'following':
        posts = posts.filter(user__in=request.user.following.all())
    elif filter_by == 'trending':
        posts = posts.order_by('-views_count', '-likes_count', '-created_at')
    else:
        posts = posts.order_by('-created_at')

    # Handle premium content
    if not request.user.is_premium:
        posts = posts.filter(
            Q(user__is_premium=False) | 
            Q(user__premium_expiry__lte=timezone.now())
        )

    # Pagination
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(page)

    return render(request, "social/feed.html", {
        "page_obj": page_obj,
        "filter_by": filter_by,
    })

@login_required
@require_POST
@transaction.atomic
def like_post(request, post_id):
    """Toggle like status with optimistic UI update"""
    try:
        post = Post.objects.select_for_update().get(id=post_id)
        
        if PostLike.objects.filter(user=request.user, post=post).exists():
            PostLike.objects.filter(user=request.user, post=post).delete()
            post.likes_count = F('likes_count') - 1
            liked = False
        else:
            PostLike.objects.create(user=request.user, post=post)
            post.likes_count = F('likes_count') + 1
            liked = True
        
        post.save()
        post.refresh_from_db()
        
        return JsonResponse({
            "status": "success",
            "liked": liked,
            "likes_count": post.likes_count
        })
    except Post.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
    except Exception as e:
        logger.error(f"Error in like_post: {str(e)}")
        return JsonResponse({"status": "error", "message": "Server error"}, status=500)

@login_required
@require_POST
def add_comment(request, post_id):
    """Add comment with form validation"""
    form = CommentForm(request.POST)
    if form.is_valid():
        try:
            with transaction.atomic():
                comment = form.save(commit=False)
                comment.post_id = post_id
                comment.user = request.user
                comment.save()

                return JsonResponse({
                    "status": "success",
                    "comment": {
                        "id": comment.id,
                        "content": comment.content,
                        "user": comment.user.username,
                        "created_at": comment.created_at.isoformat(),
                        "likes_count": 0
                    }
                })
        except Exception as e:
            logger.error(f"Error in add_comment: {str(e)}")
            return JsonResponse({"status": "error", "message": "Server error"}, status=500)
    
    return JsonResponse({"status": "error", "errors": form.errors}, status=400)

@login_required
@require_http_methods(["GET", "POST"])
def create_post(request):
    """Create post with proper validation and file handling"""
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    post = form.save(commit=False)
                    post.user = request.user
                    post.save()
                    return redirect('post_detail', post_id=post.id)
            except Exception as e:
                logger.error(f"Error in create_post: {str(e)}")
                form.add_error(None, "Error creating post. Please try again.")
    else:
        form = PostForm()
    
    return render(request, "social/post_create.html", {"form": form})

@login_required
@require_POST
def increment_view_count(request, post_id):
    """Track post views with rate limiting"""
    cache_key = f'post_view_{post_id}_{request.user.id}_{timezone.now().date()}'
    
    if not cache.get(cache_key):
        try:
            with transaction.atomic():
                post = Post.objects.select_for_update().get(id=post_id)
                PostView.objects.create(
                    post=post,
                    user=request.user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:200]
                )
                post.views_count = F('views_count') + 1
                post.save()
                
                cache.set(cache_key, True, timeout=86400)  # 24 hours
                
                return JsonResponse({"status": "success", "views_count": post.views_count})
        except Exception as e:
            logger.error(f"Error in increment_view_count: {str(e)}")
            return JsonResponse({"status": "error", "message": "Server error"}, status=500)
    
    return JsonResponse({"status": "success", "message": "View already counted"})