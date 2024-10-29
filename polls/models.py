from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings
import qrcode
from datetime import timedelta
from io import BytesIO

class Poll(models.Model):
    POLL_TYPE_CHOICES = (
        ('question', 'Question'),
        ('opinion', 'Opinion Poll'),
    )

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    poll_type = models.CharField(max_length=10, choices=POLL_TYPE_CHOICES, default='opinion')
    background_color = models.CharField(max_length=7, default="#ffffff")  # HEX color format
    show_share_button = models.BooleanField(default=True)
    link = models.URLField(max_length=200, blank=True)  # Auto-generated unique link
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)  # Track views
    expiration_time = models.DateTimeField(null=True, blank=True) 
    allow_expiration = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    banner_image = models.ImageField(upload_to='poll_banners/', blank=True, null=True)
    multi_option = models.BooleanField(default=False)  # New field for multiple selection
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set to now when created

    
    def is_active(self):
        """Checks if the poll is still active based on expiration time and allow_expiration."""
        if self.allow_expiration:
            return not self.expiration_time or timezone.now() < self.expiration_time
        return True

    def increment_view_count(self):
        """Increments the view count each time the poll is viewed."""
        print(f"Current view count: {self.view_count}")  # Debug print
        self.view_count += 1
        self.save()


    def get_absolute_url(self):
        """Returns the URL for the poll's detail view."""
        return reverse('polls:vote_poll', args=[str(self.id)])

    def generate_unique_link(self):
        """Generates a unique link to the poll based on its absolute URL."""
        self.link = f"http://127.0.0.1:8000{self.get_absolute_url()}"

    def generate_qr_code(self):
        """Generates a QR code image for the poll's unique link."""
        qr = qrcode.make(self.link)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        self.qr_code.save(f'qr_{self.id}.png', ContentFile(buffer.getvalue()), save=False)

    def total_votes(self):
        """Returns the total number of votes cast for the poll."""
        return Vote.objects.filter(poll=self).count()

    def __str__(self):
        return self.title

class Option(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=100, blank=True)  # Allow empty option_text
    is_correct = models.BooleanField(default=False)
    option_image = models.ImageField(upload_to='option_images/', blank=True, null=True)  # Optional image field

    def __str__(self):
        return self.option_text or "Option without text"  # Return something if text is empty



class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, related_name='votes', on_delete=models.CASCADE)  # Set related_name here
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=1)  # Start attempts at 1 for the first vote


    def can_vote_again(self):
        """Returns True if the user has fewer than 2 cancel attempts and the vote is within 30 minutes."""
        time_limit = timezone.now() - timedelta(minutes=30)
        return self.attempts < 2 and self.created_at >= time_limit