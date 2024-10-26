from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import F
from django.core.validators import FileExtensionValidator

def validate_file_size(value):
    filesize = value.size
    if filesize > 20 * 1024 * 1024:  # 20MB limit
        raise ValidationError("Maximum file size is 10MB")

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)  # Increased for more flexibility
    image = models.ImageField(
        upload_to='post_images/%Y/%m/',  # Organized by date
        validators=[validate_file_size],
        blank=True, 
        null=True
    )
    video = models.FileField(
        upload_to='post_videos/%Y/%m/',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi']),
            validate_file_size
        ],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0, db_index=True)
    likes_count = models.PositiveIntegerField(default=0, db_index=True)
    comments_count = models.PositiveIntegerField(default=0, db_index=True)
    likes = models.ManyToManyField(
        User, 
        related_name='liked_posts',
        through='PostLike',
        blank=True
    )
    is_boosted = models.BooleanField(default=False, db_index=True)
    boost_expires_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived')
        ],
        default='published',
        db_index=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['-created_at', 'status']),
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']

    def clean(self):
        if self.image and self.video:
            raise ValidationError("Post can't contain both image and video")
        if not (self.content or self.image or self.video):
            raise ValidationError("Post must contain either text, image, or video")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]

class PostView(models.Model):
    post = models.ForeignKey(Post, related_name='views', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    viewed_date = models.DateField(editable=False)  # New field to store the date part
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        # Set viewed_date to the date portion of viewed_at
        if not self.viewed_date:
            self.viewed_date = self.viewed_at.date()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (('post', 'user', 'viewed_date'),)
        indexes = [
            models.Index(fields=['post', '-viewed_at']),
        ]


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    likes_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Post.objects.filter(pk=self.post_id).update(
                comments_count=F('comments_count') + 1
            )

class Report(models.Model):
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('copyright', 'Copyright Violation'),
        ('violence', 'Violence'),
        ('hate_speech', 'Hate Speech'),
        ('other', 'Other'),
    ]
    
    REPORT_STATUS = [
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=REPORT_STATUS,
        default='pending'
    )
    resolved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='resolved_reports'
    )
    resolution_note = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['post', 'status']),
        ]

