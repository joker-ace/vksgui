# coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import Index, VKGetCities
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # Examples:
    url(r'^$', Index.as_view(), name='index'),
    url(r'^getvkcities/$', VKGetCities.as_view()),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()