from django.db import models
from django.conf import settings
from django.db.models import Q, Max
from django.utils import timezone

class ConversationManager(models.Manager):
    def get_or_create_conversation(self, user1, user2):
        conversations = self.filter(participants=user1).filter(participants=user2)
        if conversations.exists():
            return conversations.first(), False
        conversation = self.create()
        conversation.participants.add(user1, user2)
        return conversation, True
    
    def get_conversations_for_user(self, user):
        return self.filter(participants=user).annotate(
            last_message_time=Max('messages__timestamp'),
            unread_count=models.Count(
                'messages',
                filter=models.Q(messages__read=False) & ~models.Q(messages__sender=user)
            )
        ).order_by('-last_message_time')

class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ConversationManager()
    
    def get_last_message(self):
        return self.messages.order_by('-timestamp').first()
    
    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.save()