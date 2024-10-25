from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings
import qrcode
from io import BytesIO

class Poll(models.Model):
    POLL_TYPE_CHOICES = (
        ('question', 'Question'),
        ('opinion', 'Opinion Poll'),
    )

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    poll_type = models.CharField(max_length=10, choices=POLL_TYPE_CHOICES, default='opinion')
    background_color = models.CharField(max_length=7, default="#ffffff")  # HEX color format
    show_share_button = models.BooleanField(default=True)
    poll_language = models.CharField(max_length=20, default="English")
    link = models.URLField(max_length=200, blank=True)  # Auto-generated unique link
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)  # Track views
    expiration_time = models.DateTimeField(null=True, blank=True)
    allow_expiration = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    banner_image = models.ImageField(upload_to='poll_banners/', blank=True, null=True)
    multi_option = models.BooleanField(default=False)  # New field for multiple selection

    def is_active(self):
        """Checks if the poll is still active based on expiration time and allow_expiration."""
        if self.allow_expiration:
            return not self.expiration_time or timezone.now() < self.expiration_time
        return True

    def increment_view_count(self):
        """Increments the view count each time the poll is viewed."""
        self.view_count += 1
        self.save()

    def get_absolute_url(self):
        """Returns the URL for the poll's detail view."""
        return reverse('poll_detail', args=[str(self.id)])

    def generate_unique_link(self):
        """Generates a unique link to the poll based on its absolute URL."""
        self.link = f"{settings.SITE_URL}{self.get_absolute_url()}"

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
    option_text = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)  # Only used for "Question" polls

    def __str__(self):
        return self.option_text

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, related_name='votes', on_delete=models.CASCADE)
    option = models.ForeignKey(Option, related_name='votes', on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')  # Ensure each user can vote only once per poll
