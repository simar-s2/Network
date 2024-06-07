from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    followers = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

    def __str__(self):
        return self.username

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts_by_user', blank=True, null=True)
    timestamp = models.DateTimeField(default=now)
    likes_count = models.PositiveIntegerField(default=0)


class Like(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes_on_post', blank=True, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.id)
