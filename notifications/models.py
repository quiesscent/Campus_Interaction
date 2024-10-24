from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.contrib.auth.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("message", "New Message"),
        ("match", "New Match"),
    )

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='notification_objects')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.recipient.username}"

    def get_absolute_url(self):
        if self.notification_type == "message":
            if self.content_type.model_class().__name__ == "Message":
                message = self.content_object
                conversation = message.conversation
            elif self.content_type.model_class().__name__ == "Conversation":
                conversation = self.content_object
            else:
                return reverse("inbox")  # fallback

            other_user = conversation.participants.exclude(id=self.recipient.id).first()
            return reverse("chat_room", kwargs={"username": other_user.username})
        # Add other notification types here as needed
        return reverse("inbox")  # Default to inbox if no specific URL is available
