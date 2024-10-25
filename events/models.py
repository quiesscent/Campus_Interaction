# events/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from profiles.models import Profile  # Import the Profile model

class University(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, default='default_code')  # Set a default value

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True)
    is_event_organizer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.university or 'No University'}"  # Fixed the __str__ method

class EventCategory(models.Model):
    name = models.CharField(max_length=100, help_text="Enter the event category name.")
    description = models.TextField(blank=True, help_text="Brief description of the category.")

    class Meta:
        verbose_name_plural = "Event Categories"

    def __str__(self):
        return self.name

class EventManager(models.Manager):
    def with_status(self):
        now = timezone.now()
        return self.annotate(
            status=models.Case(
                models.When(start_date__gt=now, then=models.Value('upcoming')),
                models.When(start_date__lte=now, end_date__gte=now, then=models.Value('ongoing')),
                models.When(end_date__lt=now, then=models.Value('completed')),
                default=models.Value('cancelled'),
                output_field=models.CharField(),
            )
        )


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('physical', 'Physical Event'),
        ('text', 'Text-Based Event'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    title = models.CharField(max_length=200, help_text="Enter the event title.")
    description = models.TextField(help_text="Include the university details in this description.")
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES, default='physical')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, help_text="Event location (optional for text-based events).", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', db_index=True) # Index status
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of participants.")
    is_public = models.BooleanField(default=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True)
    
    # For text-based events
    content = models.TextField(blank=True, null=True, help_text="Content for text-based events")
    attachments = models.FileField(upload_to='event_attachments/', null=True, blank=True, help_text="Optional attachments for text-based events")
    
    objects = EventManager()  # Add custom manager

    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.start_date > now:
            self.status = 'upcoming'
        elif self.start_date <= now <= self.end_date:
            self.status = 'ongoing'
        elif self.end_date < now:
            self.status = 'completed'
        super().save(*args, **kwargs)

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'participant'], name='unique_event_participant')
        ]

    def save(self, *args, **kwargs):
        if self.event.max_participants and EventRegistration.objects.filter(event=self.event).count() >= self.event.max_participants:
            raise ValueError("Cannot register: event has reached maximum participants")
        super().save(*args, **kwargs)

class EventReaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😄'),
        ('wow', '😮'),
        ('sad', '😢'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'user', 'reaction_type'], name='unique_event_user_reaction')
        ]
    def __str__(self):
        return f"{self.user} reacted with {self.get_reaction_type_display()} on {self.event}"

class Comment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True) 
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(UserProfile, through='CommentLike', related_name='liked_comments')
    level = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.event}"

    @property
    def is_reply(self):
        return self.parent is not None

    # Added a helper method to get the comment level
    def comment_level(self):
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level
    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)
        
class CommentLike(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'comment']

    def __str__(self):
        return f"{self.user} likes {self.comment}"

class Notification(models.Model):
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Validate the existence of the related object
        if not self.content_type.model_class().objects.filter(id=self.object_id).exists():
            raise ValueError("Related object does not exist")
        super().save(*args, **kwargs)
