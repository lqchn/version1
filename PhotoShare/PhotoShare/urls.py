from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

#coding:utf8

#my import
from PhotoShare import settings

from UserClient import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'PhotoShare.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # website url
    url(r'^$', views.register),
    #register url
    url(r'^register/$', views.register),
    url(r'^user/register/$', views.user_register),

    #login url
    url(r'^login/$', views.login),
    url(r'^user/login/$', views.user_login),

    #index url
    url(r'^index/$', views.index),
    url(r'^user/info/$', views.user_index),
    url(r'^user/all/photo/$', views.get_all_photo),
    url(r'^photo/upload/user/info/$', views.get_uploadphoto_user_info),
    url(r'^comment/upload/user/info/$', views.get_comment_user_info),
    url(r'^user/comment/$', views.user_comment),
    url(r'^user/praise/$', views.user_praise),
    url(r'^user/changeinfo/$', views.user_changeinfoVersion2),
    url(r'^user/follow/$', views.user_follow),

    #pages url
    url(r'^home/$', views.pages),
    #url(r'^user/upload/$', views.upload_pic),
    url(r'^user/photo/$', views.user_photo),
    url(r'^pages/user/info/$', views.pages_user_info),
    url(r'^following/user/photo/$', views.following_user_photo),

    url(r'^user/upload/$',views.upload_picVersion2),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
    
urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
    'document_root': settings.STATIC_ROOT}))