from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse 
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit.managers import TaggableManager
# Create your models here.
def news_pic(instance,filename):
	return 'newspics/{0}/{1}'.format(instance.id,filename)

class Topics(models.Model):
	title = models.CharField(max_length=50,blank=True)
	author = models.ForeignKey(User,related_name='topics',on_delete=models.CASCADE)
	top_img = models.FileField(default="default.png",upload_to='news_pic',blank=True,null=True)
	title_time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title
	

class Newsletter(models.Model):
	topics = models.ForeignKey(Topics,related_name='topic',on_delete=models.CASCADE,null=True,blank=True)
	author = models.ForeignKey(User, related_name="news", on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add =True,null = True)
	edited = models.DateTimeField(auto_now = True,auto_now_add=False)
	title = models.CharField(max_length=250)
	content = RichTextUploadingField(null=True,blank=True)
	image = models.ImageField(default='default.png',upload_to='news_pic',null=True,blank=True,)
	nlikes = models.ManyToManyField(User,blank=True,related_name='nlike')
	tags =TaggableManager(blank=True)

	@property
	def view_count(self):
		return NewsViews.objects.filter(newsletter=self).count()

	def __str__(self):
		return self.title

class NewsViews(models.Model):
	IPAddres = models.GenericIPAddressField(default="45.243.82.169")
	newsletter = models.ForeignKey(Newsletter,related_name='nview' ,on_delete=models.CASCADE)

	def __str__(self):
		return '%r in %r news'%(self.IPAddres,self.newsletter.title)

class Comments(models.Model):
	news = models.ForeignKey(Newsletter,related_name='newsdetails',on_delete=models.CASCADE)
	newsuser = models.ForeignKey(User, related_name='newsdetails', on_delete=models.CASCADE)
	newscomment = models.CharField(max_length=2000,blank=True)
	newscomment_date = models.DateTimeField(auto_now_add=True)
	reply = models.ForeignKey('comments', on_delete=models.CASCADE, related_name="replies", null=True)