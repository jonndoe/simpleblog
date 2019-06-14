from django.contrib import admin
from .models import Subject, Post


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created']
    list_filter = ['created', 'subject']
    search_fields = ['title',]
    prepopulated_fields = {'slug': ('title',)}
