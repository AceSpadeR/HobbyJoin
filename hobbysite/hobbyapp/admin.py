from django.contrib import admin
from .models import UserProfile, Post, Chat, Message, Tag, FriendRequest

admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Tag)
admin.site.register(FriendRequest)