from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.urls import reverse
from django.conf import settings
from .forms import registerForm,ProfileUpdateForm,UserUpdateForm
from .models import Profile,FriendRequest
from feed.models import Post,comments,Like,PostImages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import random
from django.utils.timezone import now
User = get_user_model()
			
def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('feed:index'))
    else:
        if request.method != 'POST':
            form = registerForm()
        else:
            form = registerForm(data=request.POST)
            if form.is_valid():
                new_user = form.save()
                auth_login(request,new_user)
                subject = "welcome to SpaceAiro"
                message = f'Hi {request.user.username}, thank you for registering in SpaceAiro.'
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [request.user.email, ] 
                send_mail( subject, message, email_from, recipient_list )
                return redirect('users:editprofile' )
        context = {'form':form}
        return render(request,'registration/register.html',context)

@login_required
def profile_setting(request):
    return render(request,'users/profile_setting.html')
def about(request):
    return render(request,'users/about.html')


@login_required
def editprofile(request):
    if request.method !='POST':
        u_form = UserUpdateForm(instance =request.user)
        p_form = ProfileUpdateForm(instance= request.user.profile)
    else:
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(data = request.POST, files=request.FILES, instance=request.user.profile)
        cat = request.POST.getlist('check')
        c = ",".join(cat)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            pro_obj = p_form.save()
            pro_obj.feed = c
            pro_obj.save()
            return redirect('users:dashboard')
    context={'u_form':u_form,'p_form':p_form}
    return render(request,'users/editprofile.html',context)


@login_required
def profile_v(request,id):
    p = Profile.objects.get(id=id)
    u = p.user
    friends = p.friends.all()
    if p not in request.user.profile.friends.all():
        button_status = 'follow'
        post = []
    else:
        button_status = 'unfollow'
        post = Post.objects.filter(user_name=u).order_by('-date_posted')

    print(button_status)
    context = {
        'u': u,
        'friends_list': friends,
        'button':button_status,
        'post':post,
        'post_count':post.count,
        
    }

    return render(request, "users/profile.html", context)


@login_required
def dashboard(request):
    p = request.user.profile
    you = p.user
    friends = p.friends.all()
    post = Post.objects.filter(user_name=you).order_by('-date_posted')
    frequest = FriendRequest.objects.filter(to_user = you)
    for fr in frequest:
        print(fr.from_user)
        if fr.from_user not in friends:
            pass
        else:
            print(fr)
            fr.delete()

    context = {
        'u': you,
        'friends_list': friends,
        'post':post,
        'post_count':post.count,
        'frequest':frequest,
    }

    return render(request, "users/dashboard.html", context)

@login_required
def search_users(request):
    query = request.GET.get('q')
    object_list = User.objects.filter(username__icontains=query)
    context ={'users': object_list}
    return render(request, "users/search_users.html", context)
 
@login_required
def add_friends(request,id):
    user2 = get_object_or_404(User,id = id)
    user1 = request.user
    user1.profile.friends.add(user2.profile)
    if(FriendRequest.objects.filter(from_user= user2, to_user=user1).first()):
        request_rev = FriendRequest.objects.filter(from_user=user2,to_user=user1).first()
        print(request_rev)
        request_rev.delete()
    else:
        frequest,created = FriendRequest.objects.get_or_create(to_user=user2,from_user=user1)        
    return redirect('users:dashboard')

@login_required
def cancel_friend(request,id):
    user2 = get_object_or_404(User,id=id)
    user1 = request.user
    request_rev = FriendRequest.objects.filter(from_user=user2,to_user=user1).first()
    request_rev.delete()
        
    return redirect ('users:dashboard')

@login_required
def delete_friend(request,id):
    user1 = request.user
    user2= get_object_or_404(Profile,id=id)
    user1.profile.friends.remove(user2)
    #user2.profile.friends.remove(user1.profile)

    return redirect('users:profile_v', id=user2.id)

@login_required
def friend_list(request):
    p = request.user.profile
    friends = p.friends.all()
    context ={ 'friends':friends}
    return render(request,'users/friend_list.html',context)

@login_required
def users_list(request):
    return render(request,'users/users_list.html')

@login_required
def notification(request):
    friend_req = FriendRequest.objects.filter(to_user = request.user)
    print(friend_req,request.META['REMOTE_ADDR'])
    context={'frinedreq':friend_req}
    return render(request,'users/notification.html',context)