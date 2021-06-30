"""define URl patterns for users"""
from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
	path('',include('django.contrib.auth.urls')),
	# registration page
	path('register/', views.register , name="register"),
	path('accounts/profile/',views.dashboard,name='dashboard'),
    path('profile_setting/',views.profile_setting,name='profile_setting'),
    path('about/',views.about,name='about'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('search_users/',views.search_users, name='search_users'),
    path('profile_v/<int:id>/',views.profile_v , name= 'profile_v'),
    path('add_friends/<int:id>/',views.add_friends, name='add_friends'),
    path('cancel_friend/<int:id>/',views.cancel_friend,name='cancel_friend'),
    path('delete_friend/<int:id>/',views.delete_friend, name='delete_friend'),
    path('friend_list/',views.friend_list, name='friend_list'),
    path('users_list/',views.users_list,name='users_list'),
    path('notification/',views.notification,name = 'notification')
    ]