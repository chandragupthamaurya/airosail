from django.urls import path
from . import views	
from django.views.generic import TemplateView

app_name = 'newsletter'

urlpatterns = [
	path('newsletter/',views.newsletter,name="newsletter"),
	path('create_newsletter/',views.create_newsletter,name='create_newsletter'),
	path('newsdetails/<int:id>/',views.newsdetails,name='newsdetails'),
	path('editnews/<int:id>/',views.editnews,name='editnews'),
	path('deletenews/<int:id>/',views.deletenews,name='deletenews'),
	path('tagged/<slug:slug>/',views.tagged,name='tagged'),
	path('newscat/<int:id>/',views.newscat,name='newscat'),
]