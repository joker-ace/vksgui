# coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from views import Index, get_cities_by_query, run_group_parser, get_group_parsing_status, get_group_members_count, \
    get_friends_parsing_status, get_groups_by_query, run_relations_search, get_relations_search_status, run_attack, \
       get_attack_status, get_attack_results, send_notification, run_search_parser


urlpatterns = patterns('',
       url(r'^$', Index.as_view(), name='index'),
       url(r'^get_cities/$', get_cities_by_query),
       url(r'^get_groups/$', get_groups_by_query),
       url(r'^run_group_parser/$', run_group_parser),
       url(r'^run_search_parser/$', run_search_parser),
       url(r'^group_parsing_status/$', get_group_parsing_status),
       url(r'^get_group_members_count/$', get_group_members_count),
       url(r'^friends_parsing_status/$', get_friends_parsing_status),
       url(r'^run_relations_search/$', run_relations_search),
       url(r'^relations_search_status/$', get_relations_search_status),
       url(r'^run_attack/$', run_attack),
       url(r'^get_attack_status/$', get_attack_status),
       url(r'^get_attack_results/$', get_attack_results),
       url(r'^send_notification/$', send_notification),
       url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()