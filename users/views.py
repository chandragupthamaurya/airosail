from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect,Http404,JsonResponse
from django.urls import reverse
from django.conf import settings
from .forms import registerForm,ProfileUpdateForm,UserUpdateForm,ContactForm,MessageForm
from .models import Profile,FriendRequest,Messages
from feed.models import Post,comments,PostImages
from newsletter.models import Newsletter
from django.core.mail import send_mail,BadHeaderError
from django.template.loader import render_to_string,get_template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model,update_session_auth_hash 
from django.contrib.auth.forms import PasswordChangeForm
import random
from django.utils.timezone import now
from notifications.signals import notify
import notifications
from django.forms.models import model_to_dict 
import json
from feed.views import indexwork
from django.utils.html import strip_tags

User = get_user_model()
 
ind = indexwork()
class userview():
    def cat(self):
        catlist = ['agriculture','agroproducts','advertising','aerospace','ai','animation','AR VR','app','architecture',
        'arts & photography','automotive','books','car','computer vision','construnction','clothes','charity',
        'Dating','energy','entertainment','education','fitness','foods & beverages','fashion','footwear','games','green technology'
        'health','human resources','healthcare','IOT''makeup','manufacturing','non-renewable','organic','pets','property','renewable',
        'sports','smart home','software','science','technology','tutorials','trading',
        'wearable','watches','websites','yoga']
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
                message = render_to_string('emails/message.txt')
                email_from = "airo@airosail.com"
                recipient_list = [request.user.email, ] 
                try:
                    send_mail( subject, message, email_from, recipient_list )
                    return redirect('users:editprofile' )
                except:
                    return redirect('users:editprofile')
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
        error = 'Enter correct credentials or Forget the password'
        context={'error':error}
        return render( request,'registration/login.html',context)


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
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            pro_obj = p_form.save()
            pro_obj.feed = c
            pro_obj.save()
            return redirect('users:dashboard')
    context={'u_form':u_form,'p_form':p_form,'cat':cat,'feed':feed}
    return render(request,'users/editprofile.html',context)


def profile_v(request,id):
    p = Profile.objects.get(id=id)
    u = p.user
    friends = p.friends.all()
    follower = ind.followerscount(u)
    if request.user.is_authenticated:
        if p not in request.user.profile.friends.all():
            button_status = 'follow'
            post = []
        else:
            button_status = 'unfollow'
            post = Post.objects.filter(user_name=u).order_by('-date_posted')
    else:
        button_status="login"
        post = []

    context = {
        'u': u,
        'friends_list': friends,
        'button':button_status,
        'post':post,
        'post_count':post.count,
        'follower':follower,
        
    }

    return render(request, "users/profile.html", context)


@login_required
def dashboard(request):
    p = request.user.profile
    you = p.user
    friends = p.friends.all()
    post = Post.objects.filter(user_name=you).order_by('-date_posted')
    news  = Newsletter.objects.filter(author=you).order_by('-created')[:5]
    follower = ind.followerscount(request.user)
    
    context = {
        'u': you,
        'friends_list': friends,
        'post':post,
        'news':news,
        'post_count':post.count,
        'follower':follower,

    }

    return render(request, "users/dashboard.html", context)
 
@login_required
def add_friends(request,id):
    user2 = get_object_or_404(User,id = id)
    user1 = request.user
    user1.profile.friends.add(user2.profile)
    if(FriendRequest.objects.filter(from_user= user2, to_user=user1).first()):
        request_rev = FriendRequest.objects.filter(from_user=user2,to_user=user1).first()
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
        
    return redirect ('users:notification')

@login_required
def delete_friend(request,id):
    user1 = request.user
    user2= get_object_or_404(Profile,id=id)
    user1.profile.friends.remove(user2)
    #user2.profile.friends.remove(user1.profile)

    return redirect('users:profile_v', id=user2.id)

@login_required
def friend_list(request,value): #count the number of follower
    if value == 'following':
        p = request.user.profile
        friends = p.friends.all()
    else:
        friends = ind.followers(request.user) #class to get count and follower
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

def contact(request):               #contact form
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Website Inquiry" 
            body ={
            'name' : form.cleaned_data['name'],
            'email_from' : form.cleaned_data['email'],
            'message' : form.cleaned_data['content'],
            }
            email_from = form.cleaned_data['email']
            email_to = ['airosailinfo@gmail.com',] 
            message = "\n".join(body.values())
            try:
                send_mail(subject, message,email_from,email_to) 
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect ("feed:index")      
    else:
        form = ContactForm()
    context={'form':form}
    return render(request,'users/contact.html',context)
@login_required
def notification(request):    #notification tab to send notif to user
    friend_req = FriendRequest.objects.filter(to_user = request.user)
    unread = request.user.notifications.unread()
    read = request.user.notifications.read()
    note = []
    for u in unread:
        note.append(u)
    for r in read:
        note.append(r)
    for n in unread:
        n.unread = False
        n.save()
    context={'frinedreq':friend_req,'note':note}
    return render(request,'users/notification.html',context)

@login_required
def delnote(request):                         #delete the notification
    noteid = request.GET.get('noteid')
    note = request.user.notifications.get(id=noteid)
    if note:
        note.delete()
        return HttpResponse('success',True)
    else:
        return HttpResponse('unsuccess',False)

@login_required
def message(request):               #send the message form the post 
    post_id = request.POST.get('postid')
    post = Post.objects.get(id = post_id )
    if request.method== 'POST':
        message = request.POST.get('message')
        msgobject = Messages.objects.create(sender= request.user,reciver=post.user_name,message = message)
        notify.send(request.user,recipient=post.user_name,verb='send a message for %s'%(post.title),target=msgobject)
        return HttpResponse('success',True)
    else:
        return HttpResponse('unsuccess',False)

@login_required
def msg_user(request):                # send message to user from inboxmessage
    user_id = request.POST.get('user_id')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        message = request.POST.get('message')
        m = Messages.objects.create(sender= request.user,reciver=user,message = message)
        msg = m.message
    resp = {'message':msg}

    response = json.dumps(resp)
    return HttpResponse(response, content_type = "application/json")

        
@login_required
def inboxmessage(request):   #message tab in index
    wish = ind.wishlistdata(request)
    inbox = Messages.objects.filter(reciver=request.user).order_by('-msg_date')
    sendbox = Messages.objects.filter(sender= request.user).order_by('-msg_date')
    message = Messages.objects.filter(reciver=request.user).order_by('-msg_date')|Messages.objects.filter(sender=request.user).order_by('-msg_date')
    s =[]
    name = []
    for msg in sendbox:
        if msg.reciver not in name:
            s.append(msg)
            name.append(msg.reciver)
    for msg in inbox:
        if msg.sender not in name:
            s.append(msg)
            name.append(msg.sender)
    context={'inbox':inbox,
            'sendbox':sendbox,
            's':s,'wish':wish}
    return render(request,'users/messages.html',context)

@login_required
def updatemsg(request):                # it update message countinuously 6000(microsec)
    messages = Messages.objects.all().order_by('-msg_date')
    updateid = request.GET.get('updateid')
    msglist = {}
    user = User.objects.get(id = updateid)
    inbox  = Messages.objects.filter(sender = user,reciver=request.user)
    sendbox = Messages.objects.filter(reciver = user, sender= request.user)
    for i in inbox:
        msglist[i.msg_date.strftime("%m/%d/%Y,%H:%M:%S")] = model_to_dict(i)
    for s in sendbox:
        msglist[s.msg_date.strftime("%m/%d/%Y,%H:%M:%S")] = model_to_dict(s)
    msglistsort = sorted(msglist.items())
    response = json.dumps(msglistsort)
    return HttpResponse(response,content_type="application/json")

@login_required
def updatemsguser(request):
    messages = Messages.objects.all().order_by('-msg_date')
    updateid = request.GET.get('updateid')
    msglist = {}
    receviedmsg = Messages.objects.filter(reciver = request.user)
    for revmsg in receviedmsg:
        sen = revmsg.sender.username
        msgvalue = [sen,revmsg.sender.id,revmsg.message]
        msglist[revmsg.msg_date.strftime("%m%d%Y,%H:%M:%S")] = msgvalue
    msglistsort = sorted(msglist.items())
    response = json.dumps(msglistsort)
    return HttpResponse(response,content_type="application/json")


@login_required
def del_message(request):
    if request.is_ajax() and request.method=="GET":
        msgid = request.GET.get('msgid')
        user = User.objects.get(id = msgid)
        message = Messages.objects.filter(sender = user,reciver=request.user)|Messages.objects.filter(reciver= user,sender= request.user)
        message.delete()
        return HttpResponse('success',True)
    else:
        return HttpResponse('unsuccess',False)

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
        if p.user_name not in object_list:
            object_list.append(p.user_name)
    for pro in pro_list:
        if pro not in object_list:
            object_list.append(pro.user)
    context ={'users': object_list,'post':post_list}
    return render(request, "users/search_users.html", context)