from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_save
from django.conf import settings
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
profiletype = (
	('people','people'),
	('traders','Traders'),
	('company','company'),
	('Agents','Agents'),
	('others','others'),
	)
def profile_pics(instance,filename):
	return 'profilepics/{0}/{1}'.format(instance.id,filename)

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default='airosail.jpg', upload_to='profile_pics')
	slug = AutoSlugField(populate_from='user')
	bio = models.CharField(max_length=200, blank=True)
	friends = models.ManyToManyField("Profile", blank=True)
	About = models.TextField(blank=True,null=True)
	url = models.URLField(max_length=100,blank=True)
	phone = models.CharField(max_length=12,blank=True)
	address = models.CharField(max_length=200,blank=True)
	city = models.CharField(max_length=50,blank=True)
	state = models.CharField(max_length=50,blank=True)
	country = models.CharField(max_length=50,blank = True)
	profile_type =models.CharField(choices=profiletype,default='others',max_length=100)
	feed =models.CharField(max_length=500,blank=True)


	def __str__(self):
		return str(self.user.username)

	def get_absolute_url(self):
		return "/users/user/{}".format(self.slug)
def post_save_user_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
        except:
            pass

post_save.connect(post_save_user_model_receiver, sender=settings.AUTH_USER_MODEL)

class FriendRequest(models.Model):
	to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='to_user', on_delete=models.CASCADE)
	from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='from_user', on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "From {}, to {}".format(self.from_user.username, self.to_user.username)

class Messages(models.Model):
	sender = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='sender',on_delete=models.CASCADE)
	reciver =  models.ForeignKey(settings.AUTH_USER_MODEL,related_name='reciver',on_delete=models.CASCADE)
	msg_date = models.DateTimeField(auto_now_add=True)
	message = models.CharField(max_length=200,blank=True)

	def __str__(self):
		return str(self.sender)


# Create your models here.
