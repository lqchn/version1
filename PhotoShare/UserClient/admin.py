from django.contrib import admin

# Register your models here.

from UserClient.models import UserClient, Photo, Comment, Follow

admin.site.register(UserClient)

admin.site.register(Photo)

admin.site.register(Comment)

admin.site.register(Follow)

