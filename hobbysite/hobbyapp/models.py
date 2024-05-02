import os
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

def user_directory_path(instance, filename, filetag):
    extension = os.path.splitext(filename)[1]
    return 'user_{0}/{1}{2}'.format(instance.user.id, filetag, extension)

def post_directory_path(instance, filename):
    extension = os.path.splitext(filename)[1]
    return 'post_{0}/{1}{2}'.format(instance.user.id, 'post_pic', extension)

def profile_pic_directory_path(instance, filename):
    extension = os.path.splitext(filename)[1]
    return 'user_{0}/{1}{2}'.format(instance.user.id, 'profile_pic', extension)

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(
        upload_to=profile_pic_directory_path,
        default='hobbysite/media/NotFound.jpg'
    )
    color = models.CharField(max_length=7, default='#FFFFFF')
    bio = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    friends = models.ManyToManyField('self', blank=True, related_name='friends')
    chats = models.ManyToManyField('Chat', blank=True, related_name='chats')

    def __str__(self):
        return self.user.username

    def accept_friend_request(self, friend_request):
        if friend_request.to_user == self.user and friend_request.status == FriendRequest.PENDING:
            friend_request.status = FriendRequest.ACCEPTED
            friend_request.save()
            self.friends.add(friend_request.from_user.profile)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=post_directory_path, default='hobbysite/media/NotFound.jpg')
    caption = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    post_time = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f'Post by {self.user.username}'


class Chat(models.Model):
    users = models.ManyToManyField(User)
    name = models.CharField(max_length=255, null=True, blank=True)


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)



class FriendRequest(models.Model):
    PENDING = 'P'
    ACCEPTED = 'A'
    DECLINED = 'D'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    def __str__(self):
        return f'Request from {self.from_user.username} to {self.to_user.username}'

class Preferences(models.Model):
    themes = (
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=255, choices=themes)


