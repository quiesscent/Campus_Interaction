<<<<<<< HEAD
# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('DOC', 'Document'),
        ('VID', 'Video'),
        ('PDF', 'PDF'),
        ('LNK', 'Link'),
        ('OTH', 'Other')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    external_link = models.URLField(max_length=500, blank=True)
    resource_type = models.CharField(max_length=3, choices=RESOURCE_TYPES, default='DOC')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='resources')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resources')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_uploaded']

class Comment(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.resource.title}'
=======
# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('DOC', 'Document'),
        ('VID', 'Video'),
        ('PDF', 'PDF'),
        ('LNK', 'Link'),
        ('OTH', 'Other')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    external_link = models.URLField(max_length=500, blank=True)
    resource_type = models.CharField(max_length=3, choices=RESOURCE_TYPES, default='DOC')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='resources')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resources')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_uploaded']

class Comment(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.resource.title}'
>>>>>>> 7cc8ac5 (uploaded the resources app)
