"""Blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from blogs.views import UserRegisterView, UserLoginView, AddPostView, PostListView, PostDetails, UpdateDeletePost, \
    LogOutView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register_user/$', UserRegisterView.as_view(), name='register-user'),
    url(r'^login/$', UserLoginView.as_view(), name='login'),
    url(r'^add_post/$', AddPostView.as_view(), name='add_post'),
    url(r'^$', PostListView.as_view(), name='post_list'),
    url(r'^update/(?P<slug>[^/]+)/post/$', UpdateDeletePost.as_view(), name='update-post'),

    url(r'^post/(?P<slug>[^/]+)/details$', PostDetails.as_view(), name='post-details'),
    url(r'^logout/$', LogOutView.as_view(), name='logout'),
    # url(r'^login/$', UserLoginView.as_view(), name='login'),
]
