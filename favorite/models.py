from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from post.models import Post


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.user.username