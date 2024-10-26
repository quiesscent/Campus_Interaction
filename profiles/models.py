import datetime
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    year_of_study = models.IntegerField(null=True, blank=True)
    bio = models.CharField(max_length=500, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', default='profile_pics/default.png')
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Add following relationship
    following = models.ManyToManyField(
        'self',
        through='UserFollow',
        symmetrical=False,
        related_name='followers'
    )

    campus = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)

    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def was_recently_online(self):
        if not self.last_seen:
            return False
        return datetime.datetime.now(datetime.timezone.utc) - self.last_seen < datetime.timedelta(minutes=5)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def follow(self, profile_to_follow):
        if profile_to_follow != self:
            UserFollow.objects.get_or_create(
                follower=self,
                following=profile_to_follow
            )

    def unfollow(self, profile_to_unfollow):
        UserFollow.objects.filter(
            follower=self,
            following=profile_to_unfollow
        ).delete()

    def is_following(self, profile):
        return self.following.filter(id=profile.id).exists()
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['student_id']),
        ]

class UserFollow(models.Model):
    follower = models.ForeignKey(Profile, related_name='following_relationships', on_delete=models.CASCADE)
    following = models.ForeignKey(Profile, related_name='follower_relationships', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['-created_at']),
        ]