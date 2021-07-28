"""define URl patterns for users"""
from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
	path('',include('django.contrib.auth.urls')),
	# registration page
    path('newlogin/',views.newlogin,name="newlogin"),
	path('register/', views.register , name="register"),
    path('change_password/',views.cpassword,name="cpassword"),
	path('accounts/profile/',views.dashboard,name='dashboard'),
    path('profile_setting/',views.profile_setting,name='profile_setting'),
    path('contact/',views.contact,name='contact'),
    path('about/',views.about,name='about'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('search/',views.search, name='search'),
    path('profile_v/<int:id>/',views.profile_v , name= 'profile_v'),
    #add follower url path
    path('add_friends/<int:id>/',views.add_friends, name='add_friends'),
    path('cancel_friend/<int:id>/',views.cancel_friend,name='cancel_friend'),
    path('delete_friend/<int:id>/',views.delete_friend, name='delete_friend'),
    path('friend_list/<str:value>/',views.friend_list, name='friend_list'),
    path('users_list/',views.users_list,name='users_list'),
    #notification url path
    path('notification/',views.notification,name = 'notification'),
    path('delnote/',views.delnote,name='delnote'),
    #message url paths
    path('message/',views.message,name='message'),
    path('msg_user/',views.msg_user,name='msg_user'),
    path('updatemsg/',views.updatemsg,name='updatemsg'),
    path('updatemsg',views.updatemsguser,name='updatemsguser'),
    path('inboxmessage/',views.inboxmessage,name='inboxmessage'),
    path('del_message/',views.del_message,name='del_message'),
    ]