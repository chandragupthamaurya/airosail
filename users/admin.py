from django.contrib import admin

from .models import Profile, FriendRequest,Messages
# Register your models here.
admin.site.register(Profile)
admin.site.register(FriendRequest)
admin.site.register(Messages)