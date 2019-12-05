from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to='post', null=True, blank=True)
    draft = models.BooleanField(default=False)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    slug = models.SlugField(unique=True, max_length=300, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None,
                                    related_name='modified_by')

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return "{}".format(self.title)

    def get_slug(self):
        title = self.title.replace('ə', 'e').replace('ı', 'i')
        slug = slugify(title)
        unique = slug
        number = 1
        while Post.objects.filter(slug=unique).exists():
            unique = '{}-{}'.format(slug, number)
            number += 1
        return unique

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        self.slug = self.get_slug()
        return super(Post, self).save(*args, **kwargs)
