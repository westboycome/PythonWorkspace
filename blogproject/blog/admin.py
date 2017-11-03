from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Post, Tag, Category

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category','author', 'created_time', 'modified_time']

admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Category)