from django.db import models
from django.conf import settings
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    published = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_single', args=[self.id])
