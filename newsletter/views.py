from django.shortcuts import render,redirect,get_object_or_404
from .forms import NewNewsForm,NewCommentForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib.auth import get_user_model
from users.models import Profile
from notifications.signals import notify
from .models import Newsletter,NewsViews,Topics,Comments
from taggit.models import Tag
from django.core.paginator import Paginator,PageNotAnInteger, EmptyPage
from newsapi import NewsApiClient 
from django.conf import settings
import json
# Create your views here.
User = get_user_model()

def newsletter(request):
	news = Topics.objects.all()
	newslist = []
	for n in news:
		newslist.append(n.topic.all().order_by('-created')[:3])
	context = {'news':news,'newslist':newslist}
	return render(request,'news/newsletter.html',context)

@login_required
def create_newsletter(request):
	user =request.user
	if request.method == "POST":
		form = NewNewsForm(request.POST,request.FILES)
		if form.is_valid():
			obj = form.save(commit = False)
			obj.author = user
			obj.save()
		return redirect("users:dashboard")
	else:
		form  = NewNewsForm()

	context = {'form':form}

	return render(request,'news/create_newsletter.html',context)

@login_required
def editnews(request,id):
	news = Newsletter.objects.get(id =id)
	if request.method == 'POST':
		form = NewNewsForm(request.POST,request.FILES, instance = news)
		if form.is_valid():
			form.save()
		return redirect('newsletter:newsdetails' , id = id)
	else:
		form = NewNewsForm(instance = news)
	context={'form':form}
	return render(request,'news/editnews.html',context)


def newsdetails(request,id):
	news = Newsletter.objects.get(id =id)
	recentnews = Newsletter.objects.all().order_by('-created')[:3]
	relatednews = Newsletter.objects.filter(topics  = news.topics)[:3]
	newslist = []
	for recent in recentnews[:3]:
		if recent.title != news.title:
			newslist.append(recent)

	for related in relatednews:
		if related.title != news.title:
			newslist.append(related)

	topic = Topics.objects.all()
	comman_tag = Newsletter.tags.most_common()[:6]
	if request.user.is_authenticated:
		is_liked = news.nlikes.filter(id =request.user.id).exists()
	else:
		is_liked = False

	comment = Comments.objects.filter(news=news, reply= None).order_by('-newscomment_date')
	if request.method == 'POST':
		form = NewCommentForm(request.POST)
		if form.is_valid():
			reply_id = request.POST.get('reply_id')
			reply_com = None
			if reply_id:
				reply_com = Comments.objects.get(id = reply_id)
			data = form.save(commit = False)
			if request.user.is_authenticated:
				data.newsuser = request.user
				data.reply = reply_com
				data.news = news
				data.save()
			else:
				pass
			
			return redirect('newsletter:newsdetails', id = news.id)
	else:
		form = NewCommentForm()

	def get_client_ip(request):
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META['REMOTE_ADDR']
		return ip
	NewsViews.objects.get_or_create(IPAddres = get_client_ip(request),newsletter = news)

	context={'news':news,'topic':topic[:5],'newslist':newslist[ :6] ,'commantag':comman_tag,'form':form,'comment':comment,'is_liked':is_liked}
	return render(request,'news/newsdetails.html',context)

""""def newscommetadd(request):
	if request.method == "POST":
		newsid = request.POST.get('comid')
		news = Newsletter.objects.get(id =newsid)
		msg = request.POST.get('msg')
		form = NewCommentForm(request.POST)
		if form.is_valid():
			reply_id = request.POST.get('reply_id')
			reply_com = None
			if reply_id:
				reply_com = Comments.objects.get(id = reply_id)
			data = form.save(commit = False)
			if request.user.is_authenticated:
				data.commet = msg
				data.newsuser = request.user
				data.reply = reply_com
				data.news = news
				data.save()
		return HttpResponse('success')
	else:
		return HttpResponse('unsuccess')
"""
@login_required
def nlike(request):
	news_id = request.GET.get("likeId", "")
	user = request.user
	news = Newsletter.objects.get(pk=news_id)
	liked = False
	if news.nlikes.filter(id= request.user.id).exists():
		print('True')
		news.nlikes.remove(user)
	else:
		news.nlikes.add(request.user)
		liked = True
	like_count = news.nlikes.all().count()
	resp = {
        'liked':liked,
        'like_count':like_count
    }
	response = json.dumps(resp)
	return HttpResponse(response, content_type = "application/json")



def newscat(request,id):
	new = Topics.objects.get(id = id)
	news_list = new.topic.all().order_by('-created')
	paginator = Paginator(news_list,5)
	page = request.GET.get('page')
	try:
		news = paginator.page(page)
	except PageNotAnInteger:
		news =  paginator.page(1)
	except EmptyPage:
		news = paginator.page(paginator.num_pages)


	context = {'news':news,'page':page}
	return render(request,'news/newstags.html',context)

def tagged(request,slug):
	tag = get_object_or_404(Tag,slug=slug)
	news = Newsletter.objects.filter(tags= tag).order_by('-created')
	context ={'news':news}
	return render(request,'news/newstags.html',context)

def articles(request,id):
	u = User.objects.get(id = id)
	news = Newsletter.objects.filter(author = id)
	context ={'news':news,'u':u}
	return render(request,'news/articles.html',context)

@login_required
def deletenews(request,id):
	try:
		news = Newsletter.objects.get(id = id)
		news.delete()
		return redirect('users:dashboard')
	except:
		return redirect('users:dashboard')


@login_required
def del_comment(request):
	if request.is_ajax() and request.method=="GET":
		comid = request.GET.get('comid')
		comment = Comments.objects.get(id = comid)
		if comment.newsuser == request.user:
			comment.delete()
		return HttpResponse('success',True)
	else:
		return HttpResponse('unsuccess',False)


"""	newsapi = NewsApiClient(api_key =settings.NEWSAPI)
	business = {}
	blist =[]
	if newsapi: 
		if new.title == 'Business':
			business = newsapi.get_top_headlines(q='business',language='en')
		elif new.title.lower() == 'technology':
			business = newsapi.get_top_headlines(sources='techcrunch',language='en')
		else:
			business = newsapi.get_top_headlines(q='health',language='en')
		if business:
			bus = business['articles']
			bdesc =[] 
			bnews =[] 
			bimg  =[]
			burl = []
			btime = []
			bauth= []
			if bus != []:
				i=0
				while i < len(business): 
					f = bus[i]
					if f['urlToImage'] is not None:
						bnews.append(f['title']) 
						bdesc.append(f['description']) 
						bimg.append(f['urlToImage']) 
						burl.append(f['url'])
						btime.append(f['publishedAt'])
						bauth.append(f['author'])
					i += 1
				blist = zip(bnews, bdesc, bimg, burl, btime,bauth)
"""