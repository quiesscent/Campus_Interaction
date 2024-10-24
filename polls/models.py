from django.db import models
from django.contrib.auth.models import User

class Poll(models.Model):
    POLL_TYPE_CHOICES = (
        ('question', 'Question'),
        ('opinion', 'Opinion Poll'),
    )
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    poll_type = models.CharField(max_length=10, choices=POLL_TYPE_CHOICES, default='opinion')
    
    def __str__(self):
        return self.title

class Option(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=100)
    
    def __str__(self):
        return self.option_text
