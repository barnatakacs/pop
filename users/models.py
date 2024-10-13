from django.db import models
from django.contrib.auth.models import User
from posts.models import Post

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='user_profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', null=True)
    saved_posts = models.ManyToManyField(
        Post, blank=True, related_name='saved_by')

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(
        User, related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'
