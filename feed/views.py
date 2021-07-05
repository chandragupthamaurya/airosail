from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import NewPostForm,NewCommentForm,NewPostImage
from .models import Post,comments,Like,PostImages,Rating,Wishlist,PostViews
from users.models import Profile
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import json
from django.forms import modelformset_factory

from django import template
User = get_user_model()

register =  template.Library()

@register.filter()
def range(min =5):
	return range(min)
# Create your views here.
class indexwork():
	def catagories(self):
		catlist = ['agriculture','pets','architecture','arts','transport','education','trading','books','charity','energy','entertainment',
		'games','marketing','advertising','manufacturing','fashion','human','resources','photography','property','science','spiritual','technology',
		'websites',
		'app']
		return catlist

	def followers(self,user):
		friend_count=0
		user_list = Profile.objects.all() # take all profile to find the number of followers
		for ul in user_list:
			if ul.friends.filter(user=user): # check the followers
				friend_count +=1
		return friend_count

	def postlist_filter_byfeed(self,p,post,request):
		frind_post = p.friends.all() #friends list of user
		pro = p.feed.split(",") # split the user feed as array
		postlist = [] #empty list to append the filter post for this user
		for frind in frind_post:
			post_obj = Post.objects.filter(user_name=frind.user).order_by('-date_posted').first()
			postlist.append(post_obj)
		for i in post:
			if not frind_post.filter(user = i.user_name).exists():
				if i.user_name != request.user:
					ptype =i.post_type.split(",")
					for value in  ptype:
						if pro.count(value):
							postlist.append(i)				
							break
		return postlist


def index(request):
	ind = indexwork()
	incat = ind.catagories()
	p = None
	post_count=''
	follower=0
	post = Post.objects.all().order_by('-date_posted')
	postlist = Post.objects.order_by('?')
	if request.user.is_authenticated:
		post_count = Post.objects.filter(user_name=request.user) #for total post.count of user
		p = request.user.profile #user profile for frindlist
		follower = ind.followers(request.user)# indexclass
		postlist = ind.postlist_filter_byfeed(p,post,request)# index class
		
	context = {'post':postlist,'u':p,'post_count':post_count.count,'follower':follower,'cat':incat}
	return render(request,'feed/index.html',context)


@login_required
def create_post(request):
	ind = indexwork()
	user = request.user
	if request.method == 'POST':
		p_form = NewPostForm(request.POST)
		i_form = NewPostImage(request.POST, request.FILES)
		files = request.FILES.getlist('images') # get all the files from the post
		cat = request.POST.getlist('check')#take a list from the from in creat post 
		c = ",".join(cat) # change the array to string
		if p_form.is_valid() and i_form.is_valid():
			p_obj = p_form.save(commit=False)
			p_obj.post_type = c # save that string
			p_obj.user_name = user
			p_obj.save()
			for f in files[0:4]: # save the 4 images to post 
				if f:
					photo = PostImages(Imgtitle=p_obj, pimages=f)
					photo.save()
			messages.success(request,"Yeeew, check it out on the home page!")
			return redirect("users:dashboard")
	else:
		p_form = NewPostForm()
		i_form = NewPostImage()
	context = {'postForm': p_form, 'imageform': i_form,'cat':ind.catagories()}
	return render(request, 'feed/create_post.html',context)



@login_required
def editpost(request,id):
	ind = indexwork()
	details = Post.objects.get(id= id)
	photos = PostImages.objects.filter(Imgtitle= details)
	feed = details.post_type.split(",")
	if request.method != 'POST':
		p_form = NewPostForm(instance = details)
		i_form = NewPostImage()
	else:
		p_form = NewPostForm(instance= details,data=request.POST)
		i_form = NewPostImage(request.POST or None,request.FILES or None)
		cat = request.POST.getlist('check')
		c = ','.join(cat)
		files = request.FILES.getlist('images')
		if p_form.is_valid() and i_form.is_valid():
			pro = p_form.save()
			pro.post_type = c
			pro.save()
			if len(photos) < 4:
				a = 4-len(photos)
				for f in files[0:a]:
					photo = PostImages(Imgtitle = details,pimages=f)
					photo.save()
				return redirect('feed:postdetails',id =id)
			return redirect('feed:postdetails',id =id)
	context = {'postform':p_form,'imageform':i_form,'det':details,'img':photos,'cat':ind.catagories(),'feed':feed}
	return render(request,'feed/editpost.html',context)

def postdetails(request,id):
	post = Post.objects.get(id=id)
	photo = PostImages.objects.filter(Imgtitle=post)
	def get_client_ip(request):
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META['REMOTE_ADDR']
		return ip
	PostViews.objects.get_or_create(IPAddres = get_client_ip(request),post=post)

	if request.user.is_authenticated:
		is_wished = Wishlist.objects.filter(user = request.user ,post = post)
		is_liked = Like.objects.filter(user = request.user,post=post)
	else:
		is_wished = None
		is_liked = None
	comment = comments.objects.filter(post=post, reply= None).order_by('-id')
	rate = Rating.objects.filter(post = post)
	a=0
	for r in rate:
		a += r.rating
	if len(rate)==0:
		b = 0
	else:
		b = (a/len(rate))/10

	if request.method == 'POST':
		form = NewCommentForm(request.POST)
		if form.is_valid():
			reply_id = request.POST.get('reply_id')
			print(reply_id)
			reply_com = None
			if reply_id:
				reply_com = comments.objects.get(id = reply_id)
			data = form.save(commit = False)
			if request.user.is_authenticated:
				data.username = request.user
				data.reply = reply_com
				data.post = post
				data.save()
			else:
				pass
			
			return redirect('feed:postdetails', id = post.id)
	else:
		form = NewCommentForm()
	context = {'post':post,'photo':photo,'form':form,'is_wished':is_wished,'is_liked':is_liked,'comment':comment,'ratevalue':round(b,2),} 
	return render(request,'feed/postdetails.html',context)

@login_required
def deletepost(request,id):
	post = Post.objects.get(id = id)
	post.delete()
	return redirect('users:dashboard')

def categories(request):
	value = request.GET.get('cvalue')
	post = Post.objects.all()
	postlist =[]
	for p in post:
		cate = p.post_type.split(",")
		for c in cate:
			if c == value:
				postlist.append(p)

	
	context = {"allpost":postlist}
	return render(request,'feed/products.html',context)

@login_required
def changeimage(request,imgid,postid,value):
	print(imgid,postid)
	photo = PostImages.objects.get(id = imgid)
	if value == 'change':
		file = request.FILES['images']
		print(photo.pimages)
		print(file)
		photo.pimages = file
		photo.save()
	else:
		photo.delete()
		
	return redirect('feed:editpost',id = postid )

def comment_list(request,id):
	post = Post.objects.get(id=id)
	comment = comments.objects.filter(post=post, reply= None).order_by('-id')
	if request.method == 'POST':
		form = NewCommentForm(request.POST)
		if form.is_valid():
			reply_id = request.POST.get('reply_id')
			print(reply_id)
			reply_com = None
			if reply_id:
				reply_com = comments.objects.get(id = reply_id)
			data = form.save(commit = False)
			if request.user.is_authenticated:
				data.username = request.user
				data.reply = reply_com
				data.post = post
				data.save()
			else:
				pass
			
			return redirect('feed:comment_list', id = post.id)
	else:
		form = NewCommentForm()

	context={'post':post,'form':form,'comment':comment}
	return render(request,'feed/comment.html',context)

@login_required
def del_comment(request):
	if request.is_ajax() and request.method=="GET":
		comid = request.GET.get('comid')
		comment = comments.objects.get(id = comid)
		if comment.username == request.user:
			comment.delete()
		return HttpResponse('success',True)
	else:
		return HttpResponse('unsuccess',False)

@login_required
def like(request):
	post_id = request.GET.get("likeId", "")
	user = request.user
	post = Post.objects.get(pk=post_id)
	liked= False
	like = Like.objects.filter(user=user, post=post)
	if like:
		like.delete()
	else:
		liked = True
		Like.objects.create(user=user, post=post)
	like_count = post.likes.all().count()
	resp = {
        'liked':liked,
        'like_count':like_count
    }
	response = json.dumps(resp)
	return HttpResponse(response, content_type = "application/json")

def wish(request):
	post_id = request.GET.get("wishId", "")
	user = request.user
	post = Post.objects.get(pk=post_id)
	wished= False
	wish = Wishlist.objects.filter(user=user, post=post)
	if wish:
		wish.delete()
	else:
		wished = True
		Wishlist.objects.create(user=user, post=post)
	resp = {
        'wished':wished
    }
	response = json.dumps(resp)
	return HttpResponse(response, content_type = "application/json")
@login_required
def deletelike(request,id):
	wish = Wishlist.objects.get(id = id)
	if wish.user == request.user:
		wish.delete()
	return redirect('feed:wishlist')

@login_required
def wishlist(request):
	p = request.user.profile
	wish = Wishlist.objects.filter(user=request.user)
	context ={'wish':wish }
	return render(request,'feed/wishlist.html',context)

@login_required
def ratingstar(request):
	post_id = request.GET.get("rateid",)
	value = request.GET.get("ratevalue",)
	user = request.user
	post = Post.objects.get(id = post_id)
	print(post_id,value)
	rate = Rating.objects.filter(user = user,post= post)
	if rate:
		for r in rate:
			r.rating = value
			r.save()
	else:
		Rating.objects.create(user = user , post= post)
	resp = {
        'rated':True
    }
	response = json.dumps(resp)
	return HttpResponse(response, content_type = "application/json")

def rules(request,value):
	if value == "about":
		context={'about':value}
	elif value == "privacy":
		context = {'privacy':value}
	else:
		context={'condition':value}
	return render(request,'feed/rules.html',context)
def reports(request,id):
		
	return render(request,'feed/wishlist.html')