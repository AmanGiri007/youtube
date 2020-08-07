from django.contrib import admin

# Register your models here.
from .models import Video,Channel,Comment
admin.site.register([Video,Comment,Channel])