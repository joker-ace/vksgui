# coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from views import Index, VKGetCities, VKGetGroups, VKGroupParser, VKGroupParserChecker, VKGetParsedMembersCount, \
    VKGroupMembersFriendsChecker


urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', Index.as_view(), name='index'),
                       url(r'^getvkcities/$', VKGetCities.as_view()),
                       url(r'^getvkgroups/$', VKGetGroups.as_view()),
                       url(r'^rungroupparsing/$', VKGroupParser.as_view()),
                       url(r'^checkgroupparsingstatus/$', VKGroupParserChecker.as_view()),
                       url(r'^getparsedmemberscount/$', VKGetParsedMembersCount.as_view()),
                       url(r'^checkgroupmembersfriendsparsingstatus/$', VKGroupMembersFriendsChecker.as_view()),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()