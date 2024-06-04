from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    followers = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

    def __str__(self):
        return self.username

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "followers": list(self.followers.values_list('username', flat=True)),
            "following": list(self.followed_by.values_list('id', flat=True)),
            "followers_count": self.followers.count(),
            "following_count": self.followed_by.count(),
            "posts": list(self.posts_by_user.values_list('id', flat=True)),
        }

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts_by_user', blank=True, null=True)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return self.title

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "username": self.user_id.username,
            "timestamp": self.timestamp,
        }

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments_on_post', blank=True, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_by_user', blank=True, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return self.post_id

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "user_id": self.user_id.username,
            "timestamp": self.timestamp,
        }

class Like(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes_on_post', blank=True, null=True)
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes_on_comment', blank=True, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return self.post_id and self.comment_id

    def serialize(self):
        return {
            "id": self.id,
            "post_id": self.post_id.id,
            "comment_id": self.comment_id.id,
            "user_id": self.user_id.username,
            "timestamp": self.timestamp,
        }
