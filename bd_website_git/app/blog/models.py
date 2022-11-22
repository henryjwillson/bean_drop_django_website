from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from django.conf import settings


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    header_image = models.ImageField(
        null=True, blank=True, default='default.jpg', upload_to='post_pics')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)

        if settings.DEBUG:
            img = Image.open(self.header_image.path)
            if img.height > 800 or img.width > 800:
                height_output = (img.height/(img.width/800))
                output_size = (800, height_output)
                img.thumbnail(output_size)
                img.save(self.header_image.path)
        else:
            img = Image.open(self.header_image.name)
            if img.height > 800 or img.width > 800:
                height_output = (img.height/(img.width/800))
                output_size = (800, height_output)
                img.thumbnail(output_size)
                img.save(self.header_image.name)

