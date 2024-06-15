from django.contrib.auth.models import User
from django.db.models import Count

from .models import UserProfile, Message, Chat, Post, FriendRequest, Tag
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import RegistrationForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from .forms import PostForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'The Sign up was successful. Thank you, {username}.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'hobbyapp/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/')

@login_required()
def posts_view(request):
    posts_objects = Post.objects.all().order_by('-post_time')
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    #posts = user_profile.user.post_set.all()
    tag = request.GET.get('tag')
    if tag != '' and tag is not None:
        posts_objects = posts_objects.filter(tags__name__icontains=tag)
    paginator = Paginator(posts_objects, 5)
    page = request.GET.get('page')
    posts_objects = paginator.get_page(page)
    return render(request, 'hobbyapp/posts.html', {'posts_objects': posts_objects, 'user_profile': user_profile})


@login_required()
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()
            return redirect('post_view')
    else:
        form = PostForm()
    return render(request, 'hobbyapp/addpost.html', {'form': form})

@login_required
def add_friend(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        user = User.objects.get(id=request.user)
        friend_request, created = FriendRequest.objects.get_or_create(
            from_user=request.user,
            to_user=user)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        username = request.GET.get('username')
        if username:
            users = User.objects.filter(username__icontains=username).exclude(id=request.user.id)
        else:
            users = User.objects.all().exclude(id=request.user.id)
        friend_requests = FriendRequest.objects.filter(to_user=request.user, status=FriendRequest.PENDING)
        sent_requests = request.user.sent_requests.all()
        received_requests = request.user.received_requests.all()
        all_requests = list(sent_requests) + list(received_requests)
        request_status = {req.to_user.id if req.from_user == request.user else req.from_user.id: req.status for req in all_requests}
        current_user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        sent_request_ids = sent_requests.values_list('to_user__id', flat=True)
        received_request_ids = received_requests.values_list('from_user__id', flat=True)
        for user in users:
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            if user_profile in current_user_profile.friends.all() or current_user_profile in user_profile.friends.all():
                user.status = 'A'
            elif user.id in sent_request_ids:
                user.status = 'P'
            elif user.id in received_request_ids:
                user.status = 'P'
            else:
                user.status = 'N'
        context = { 'user_profile': user_profile,
                    'users': users,
                   'friend_requests': friend_requests,
                   'sent_requests': sent_requests,
                   'received_requests': received_requests,
                   'request_status': request_status}
        return render(request, 'hobbyapp/addfriend.html', context)


@login_required()
def send_friend_request(request, user_id):
    if request.user.is_authenticated:
        user = User.objects.get(id=user_id)
        friend_request, created = FriendRequest.objects.get_or_create(
            from_user=request.user,
            to_user=user)
        return redirect('add_friend')


@login_required()
def accept_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)
    if friend_request.to_user == request.user:
        to_user_profile = UserProfile.objects.get(user=friend_request.to_user)
        from_user_profile = UserProfile.objects.get(user=friend_request.from_user)
        to_user_profile.friends.add(from_user_profile)
        friend_request.delete()
        return redirect('add_friend', user_id=request.user.id)
    else:
        return HttpResponse("You can't accept a friend request that isn't yours.")

@login_required()
def decline_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)
    if friend_request.to_user == request.user:
        friend_request.delete()
        return redirect('add_friend', user_id=request.user.id)
    else:
        return HttpResponse("You can't decline a friend request that isn't yours.")

@login_required()
def chat_view(request, user_id, chat_id):
    user_profile = UserProfile.objects.get(user_id=user_id)
    chat = Chat.objects.get(id=chat_id)
    messages = Message.objects.filter(chat=chat)
    users = chat.users.all()

    if request.method == 'POST':
        content = request.POST.get('message')
        new_message = Message.objects.create(chat=chat, user=request.user, content=content)
        new_message.save()
        return redirect('chat_view', user_id=request.user.id, chat_id=chat.id)

    context = {'messages': messages, 'users': users, 'user_profile': user_profile,}
    return render(request, 'hobbyapp/chats.html', context)


@login_required()
def create_chat(request, friend_id):
    friend = User.objects.get(id=friend_id)
    chats = Chat.objects.annotate(user_count=Count('users'))
    chat = chats.filter(users__in=[request.user, friend], user_count=2).first()
    if chat is None:
        chat = Chat.objects.create()
        chat.users.add(request.user, friend)
    return redirect('chat_view', user_id=request.user.id, chat_id=chat.id)

@login_required()
def profile_view(request, user_id):
    user_profile = UserProfile.objects.get(user_id=user_id)
    posts = user_profile.user.post_set.all()
    context = {
        'user_profile': user_profile,
        'posts': posts,
    }
    return render(request, 'hobbyapp/profile.html', context)

@login_required()
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_view')


@login_required()
def edit_profile_view(request, user_id):
    user_profile = UserProfile.objects.get(user_id=user_id)
    if request.user.id != user_id:
        return HttpResponseForbidden("You are not allowed to edit this profile.")
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=user_id)
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'hobbyapp/editProfile.html', {'form': form})
