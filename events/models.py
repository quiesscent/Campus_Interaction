from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from profiles.models import Profile  # Use the Profile model from profiles app


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

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError('Start date must be before end date.')

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('physical', 'Physical Event'),
        ('text', 'Text-Based Event'),
    ]
    
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    title = models.CharField(max_length=200, help_text="Enter the event title.")
    description = models.TextField(help_text="Event description")
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES, default='physical')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, help_text="Event location (optional for text-based events).", blank=True, null=True)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of participants.")
    is_public = models.BooleanField(default=True)
    campus = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='campus_events')
    organizer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='organized_events')

    # For text-based events
    content = models.TextField(blank=True, null=True, help_text="Content for text-based events")
    attachments = models.FileField(upload_to='event_attachments/', null=True, blank=True)
    
    objects = EventManager()

    def save(self, *args, **kwargs):
        if not self.campus and self.organizer:
            self.campus = self.organizer
        super().save(*args, **kwargs)
        
class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Use Profile here
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
class Comment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_comments')  # Profile is used here
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(Profile, through='CommentLike', related_name='liked_comments')  # Profile is used here
    level = models.PositiveIntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    path = models.TextField(editable=False, db_index=True, default="")  # Used for ordering hierarchical comments

    class Meta:
        ordering = ['path']  # Orders by hierarchical path for displaying replies under parent comments

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set path for new comments
            self.path = f"{self.parent.path if self.parent else ''}/{self.pk or ''}".strip('/')
            self.level = (self.parent.level + 1) if self.parent else 0
        else:
            self.is_edited = True
        super().save(*args, **kwargs)

class CommentLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Profile is used here
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'comment']  # Ensures one like per user-comment pair

    def __str__(self):
        return f"{self.user} likes {self.comment}"

class EventReaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😄'),
        ('wow', '😮'),
        ('sad', '😢'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Use Profile here
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'user', 'reaction_type'], name='unique_event_user_reaction')
        ]

    def __str__(self):
        return f"{self.user} reacted with {self.get_reaction_type_display()} on {self.event}"
