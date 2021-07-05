from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.urls import reverse
from django.conf import settings
from .forms import registerForm,ProfileUpdateForm,UserUpdateForm,ContactForm
from .models import Profile,FriendRequest
from feed.models import Post,comments,Like,PostImages
from django.core.mail import send_mail,BadHeaderError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model,update_session_auth_hash 
from django.contrib.auth.forms import PasswordChangeForm
import random
from django.utils.timezone import now
User = get_user_model()

class userview():
    def cat(self):
        catlist = ['agriculture','pets','architecture','arts','transport','education','trading','books','charity','energy','entertainment',
        'games','marketing','advertising','manufacturing','fashion','human','resources','photography','property','science','spiritual','technology',
        'websites','app',]
        return catlist

uv= userview()
			
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

def newlogin(request):
    if request.method == "POST":
        email = request.POST['username']
        raw_password = request.POST['password']

        try:
            account = authenticate(username=User.objects.get(email=email).username,password=raw_password)
            if account is not None:
                auth_login(request,account)
                return redirect('users:dashboard')
        except:
            account = authenticate(username=email, password=raw_password)
            if account is not None:
                auth_login(request, account)
                return redirect('users:dashboard')
        return render( request,'registration/login.html')


def cpassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:cpassword')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    context={
        'form': form
    }
    return render(request, 'registration/cpassword.html', context)

@login_required
def profile_setting(request):
    return render(request,'users/profile_setting.html')

def about(request):
    return render(request,'users/about.html')
@login_required
def editprofile(request):
    cat = uv.cat()
    feed = None
    if request.method !='POST':
        u_form = UserUpdateForm(instance =request.user)
        p_form = ProfileUpdateForm(instance= request.user.profile)
        feed = request.user.profile.feed.split(",")
    else:
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(data = request.POST, files=request.FILES, instance=request.user.profile)
        cat = request.POST.getlist('check')
        c = ",".join(cat)
        print(c)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            pro_obj = p_form.save()
            pro_obj.feed = c
            pro_obj.save()
            return redirect('users:dashboard')
    context={'u_form':u_form,'p_form':p_form,'cat':cat,'feed':feed}
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
        if fr.from_user not in friends:
            pass
        else:
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
def add_friends(request,id):
    user2 = get_object_or_404(User,id = id)
    user1 = request.user
    user1.profile.friends.add(user2.profile)
    if(FriendRequest.objects.filter(from_user= user2, to_user=user1).first()):
        request_rev = FriendRequest.objects.filter(from_user=user2,to_user=user1).first()
        print(request_rev)
        request_rev.delete()
    else:
        if user2.profile.profile_type == 'people':
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
    post_feed =[]
    user_feed = request.user.profile.feed
    feed = user_feed.split(",")
    post_list =Post.objects.all()
    for p in post_list:
        for f in feed:
            if f in p.post_type.split(","):
                if not post_feed.count(p.user_name.profile):
                    post_feed.append(p.user_name.profile)
    context={"post_feed":post_feed}
    return render(request,'users/users_list.html',context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Website Inquiry" 
            message = form.cleaned_data['content']
            email_from = form.cleaned_data['email']
            email_to= settings.EMAIL_HOST_USER 
            try:
                send_mail(subject, message, email_from,email_to) 
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect ("feed:index")      
    else:
        form = ContactForm()
    context={'form':form}
    return render(request,'users/contact.html',context)
@login_required
def notification(request):
    friend_req = FriendRequest.objects.filter(to_user = request.user)
    anylike = Post.objects.filter(user_name = request.user)
    context={'frinedreq':friend_req}
    return render(request,'users/notification.html',context)

def search(request):
    object_list =[]
    query = request.GET.get('q')
    user_list = User.objects.filter(username__icontains=query)
    pro_list= Profile.objects.filter(state__icontains=query)|Profile.objects.filter(country__icontains=query)
    post_list =Post.objects.filter(title__icontains=query)
    for u in user_list:
        if u not in object_list:
            object_list.append(u)
    for p in post_list:
        if p not in object_list:
            object_list.append(p)
    for pro in pro_list:
        if pro not in object_list:
            object_list.append(pro.user)
    print(object_list)    
    context ={'users': object_list,'post':post_list}
    return render(request, "users/search_users.html", context)