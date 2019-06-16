from django.db import models
from django.contrib.auth import get_user_model

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .fields import OrderField

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from imagekit import ImageSpec
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, Adjust, ResizeToFit
from app_posts.processors import Watermark


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Post(models.Model):
    owner = models.ForeignKey(get_user_model(),
                              related_name='posts_created',
                              on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,
                                related_name='posts',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created']

    def __str__(self):
        return  self.title



class Content(models.Model):
    post = models.ForeignKey(Post,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in':(
                                         'text',
                                         'video',
                                         'image',
                                         'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['post'])

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    owner = models.ForeignKey(get_user_model(),
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def render(self):
        return render_to_string('posts/content/{}.html'.format(
            self._meta.model_name), {'item': self})

    def __str__(self):
        return self.title


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    #file = models.FileField(upload_to='images')
    file = ProcessedImageField(upload_to="images",
                                 #blank=True,
                                 processors=[
                                     ResizeToFit(1300,1300, upscale=False),
                                     Watermark(),
                                 ],
                                 format='JPEG',
                                 options={'quality': 60})

    thumbnail = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFill(300, 200)], source='file',
            format='JPEG', options={'quality': 100})


class Video(ItemBase):
    url = models.URLField()

