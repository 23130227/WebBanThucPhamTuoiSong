from django.db import models
from django.urls import reverse


# Create your models here.
class HomeSlide(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    background_image = models.ImageField(upload_to='home_slides/')
    button_text = models.CharField(max_length=100, blank=True, default='Xem chi tiết')
    button_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
