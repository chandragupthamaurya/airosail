from django.urls import path
from . import views	
from django.views.generic import TemplateView

app_name = 'feed'

urlpatterns = [
    path('',views.index,name = 'index'),
    path('create_post/',views.create_post,name = 'create_post'),
    path('editpost/<int:id>/',views.editpost,name='editpost'),
    path('postdetials/<int:id>/',views.postdetails,name='postdetails'),
    path('tagged/<slug:slug>/',views.tagged,name='tagged'),
    path('deletepost/<int:id>/',views.deletepost,name= 'deletepost'),
    path('changeimage/<int:imgid>/<int:postid>/<str:value>/',views.changeimage, name='changeimage'),
	path('like/', views.like, name='post-like'),
    path('wish/', views.wish, name='wish'),
	path('deletelike/<int:id>',views.deletelike, name = 'deletelike'),
	path('del_comment/',views.del_comment,name = 'del_comment'),
    path('comment_list/<int:id>/',views.comment_list,name='comment_list'),
	path('categories/',views.categories,name = 'categories'),
	path('wishlist/',views.wishlist,name='wishlist'),
	path('ratingstar/',views.ratingstar,name='ratingstar'),
    path('rules/<str:value>/',views.rules,name='rules'),
    path('reports/<int:id>/',views.reports,name="reports"),
    path('search/',views.search,name="search"),

    ]