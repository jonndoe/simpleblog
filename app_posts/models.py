from django.db import models
from django.contrib.auth import get_user_model

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .fields import OrderField

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils import timezone

from imagekit import ImageSpec
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, Adjust, ResizeToFit
from app_posts.processors import Watermark

from django.urls import reverse

from taggit.managers import TaggableManager


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,
                     self).get_queryset()\
                          .filter(status='published')



class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    owner = models.ForeignKey(get_user_model(),
                              related_name='posts_created',
                              on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,
                                related_name='posts',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')
    postavatar = ProcessedImageField(upload_to="postavatars/%Y/%m/%d/",
                               blank=True,
                               processors=[
                                   ResizeToFit(1600, 500,
                                               #upscale=False
                                               ),
                                   Watermark(),
                               ],
                               format='JPEG',
                               options={'quality': 60})

    objects = models.Manager() # the default manager
    published = PublishedManager() # Custom manager
    tags = TaggableManager()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return  self.title

    #def get_absolute_url(self):
       # return reverse('post_detail_absolute',
       #                args=[self.publish.year,
        #                     self.publish.month,
        #                     self.publish.day,
       #                      self.slug])


class MyComment(models.Model):
    owner = models.ForeignKey(get_user_model(),
                              on_delete=models.CASCADE,
                              related_name='mycomments')
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='mycomments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)




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

