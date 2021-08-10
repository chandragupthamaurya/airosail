from django.shortcuts import render,redirect,get_object_or_404
from .forms import NewNewsForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib.auth import get_user_model
from users.models import Profile
from notifications.signals import notify
from .models import Newsletter,NewsViews,Topics
from taggit.models import Tag
from django.core.paginator import Paginator,PageNotAnInteger, EmptyPage
from newsapi import NewsApiClient 
from django.conf import settings

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
	newslist = Newsletter.objects.all().order_by('-created')
	topic = Topics.objects.all()
	comman_tag = Newsletter.tags.most_common()[:6]
	def get_client_ip(request):
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META['REMOTE_ADDR']
		return ip
	NewsViews.objects.get_or_create(IPAddres = get_client_ip(request),newsletter = news)


	context={'news':news,'topic':topic[:5],'newslist':newslist[ :6] ,'commantag':comman_tag}
	return render(request,'news/newsdetails.html',context)

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

	newsapi = NewsApiClient(api_key =settings.NEWSAPI) 
	if new.title.lower() == 'business':
		business = newsapi.get_top_headlines(q='business',language='en')
	elif new.title.lower() == 'technology':
		business = newsapi.get_top_headlines(sources='techcrunch',language='en')
	else:
		business = newsapi.get_top_headlines(q='health',language='en')


	bus = business['articles']
	bdesc =[] 
	bnews =[] 
	bimg  =[]
	burl = []
	btime = []
	bauth= []

	for i in range(8): 
		f = bus[i]
		if f['urlToImage'] is not None:
			bnews.append(f['title']) 
			bdesc.append(f['description']) 
			bimg.append(f['urlToImage']) 
			burl.append(f['url'])
			btime.append(f['publishedAt'])
			bauth.append(f['author'])
	blist = zip(bnews, bdesc, bimg, burl, btime,bauth)

	context = {'news':news,'page':page,'bus':blist}
	return render(request,'news/newstags.html',context)

def tagged(request,slug):
	tag = get_object_or_404(Tag,slug=slug)
	news = Newsletter.objects.filter(tags= tag).order_by('-created')
	context ={'news':news}
	return render(request,'news/newstags.html',context)

@login_required
def deletenews(request,id):
	try:
		news = Newsletter.objects.get(id = id)
		news.delete()
		return redirect('users:dashboard')
	except:
		return redirect('users:dashboard')


