"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from myapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('first_chat/top/', views.top, name='top'),
    path('first_chat/signup/', views.signup, name='signup'),
    path('first_chat/home/', views.home, name='home'),
    path('first_chat/report_healthcheck_notification/', views.report_healthcheck_notification, name='report_healthcheck_notification'),
    path('first_chat/login/', auth_views.LoginView.as_view(), name='login'),
    path('first_chat/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('first_chat/chats/<int:friend_id>/', views.chat_with_friend, name='chat_with_friend'), 
    path('first_chat/send_stamp/', views.send_stamp, name='send_stamp'),
    path('first_chat/chats/', views.chat_list, name='chat_list'),
    path('first_chat/update_friend/<int:friend_id>/', views.update_friend, name='update_friend_info'), 
    path('first_chat/lists/', views.friend_list, name='friend_list'),
    path('first_chat/adds/', views.add_friend, name='add_friend'),
    path('first_chat/notifies/', views.notify_list, name='notify_list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#開発中に使用、完成したら削除していい
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)