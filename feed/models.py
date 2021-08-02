from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse 
from ckeditor.fields import RichTextField
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit.managers import TaggableManager
# Create your models here.
currency_type=(
	('INR ₹','INR'),
	('USD $','USD'),
)
def post_pic(instance,filename):
	return 'postpics/{0}/{1}'.format(instance.id,filename)

class Post(models.Model):
	title = models.CharField(max_length = 255)
	descriptions =RichTextField(null=True,blank =True)
	date_posted = models.DateTimeField(auto_now_add=True)
	user_name = models.ForeignKey(User,on_delete=models.CASCADE)
	currency = models.CharField(choices=currency_type,default='INR',max_length=6)
	price = models.IntegerField(null= True,blank=True)
	buyurl = models.URLField(max_length=255,blank=True,null=True)
	tags =TaggableManager(blank=True)
	post_type = models.CharField(max_length=300,blank=True,null=True)
	likes = models.ManyToManyField(User,blank=True,related_name='like')
	wishlist = models.ManyToManyField(User,blank=True,related_name='wish')
	timer = models.DateTimeField(null=True,blank=True)
	percentage = models.IntegerField(null=True,blank=True)

	@property
	def view_count(self):
		return PostViews.objects.filter(post=self).count()
	

	def __str__(self):
		return self.title

class PostImages(models.Model):
	Imgtitle = models.ForeignKey(Post,related_name='img',on_delete=models.CASCADE)
	pimages = models.FileField(upload_to='post_pic',null=True,blank=True)

class PostViews(models.Model):
	IPAddres = models.GenericIPAddressField(default="45.243.82.169")
	post = models.ForeignKey(Post,related_name='pview' ,on_delete=models.CASCADE)

	def __str__(self):
		return '%r in %r post'%(self.IPAddres,self.post.title)

class comments(models.Model):
	post = models.ForeignKey(Post,related_name='details',on_delete=models.CASCADE)
	username = models.ForeignKey(User, related_name='details', on_delete=models.CASCADE)
	comment = models.CharField(max_length=2000,blank=True)
	comment_date = models.DateTimeField(auto_now_add=True)
	reply = models.ForeignKey('comments', on_delete=models.CASCADE, related_name="replies", null=True)

class Rating(models.Model):
	user = models.ForeignKey(User,related_name='rates', on_delete=models.CASCADE)
	post = models.ForeignKey(Post,related_name='rates', on_delete=models.CASCADE)
	rating = models.IntegerField(default=0,
		validators =[
		MaxValueValidator(5),
		MinValueValidator(0)
		])

