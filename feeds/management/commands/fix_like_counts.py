from django.core.management.base import BaseCommand
from django.db.models import Count
from feeds.models import Post, PostLike

class Command(BaseCommand):
    help = 'Fix post like counts'

    def handle(self, *args, **options):
        # Update all posts' like counts
        posts = Post.objects.annotate(
            actual_likes=Count('postlike')
        ).all()

        for post in posts:
            if post.likes_count != post.actual_likes:
                Post.objects.filter(id=post.id).update(
                    likes_count=post.actual_likes
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fixed post {post.id}: {post.likes_count} -> {post.actual_likes}'
                    )
                )