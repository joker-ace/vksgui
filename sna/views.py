# coding=utf-8
import requests
from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from utils import json_response
from sna.celery import app
import sna.tasks


class Index(View):
    def get(self, request, *args, **kwargs):
        countries = {
            '1': 'Россия',
            '2': 'Украина'
        }

        return render_to_response("index.html", {"countries": countries},
                                  RequestContext(request))


class VKGetGroups(View):
    def post(self, request, *args, **kwargs):
        query = request.POST.get('query', '')
        if query == '':
            json_response(0)

        group_type = request.POST.get('type', '')

        data = {
            'v': settings.API_VERSION,
            'access_token': settings.VK_API_TOKEN,
            'q': query,
            'count': 1000,
            'type': group_type
        }

        url = settings.GET_GROUPS_URL
        r = requests.post(url, data=data)
        groups_data = r.json()
        if u'response' in groups_data:
            return json_response(groups_data[u'response']['items'])

        return json_response(0)


class VKGetCities(View):
    def post(self, request, *args, **kwargs):
        countryId = int(request.POST.get('country', 0))
        if countryId == 0:
            return json_response(0)

        data = {
            'country_id': countryId,
            'v': settings.API_VERSION,
            'access_token': settings.VK_API_TOKEN
        }

        query = request.POST.get('query', None)
        if query:
            data['q'] = query

        url = settings.GET_CITIES_URL
        r = requests.post(url, data=data)

        cities_data = r.json()
        items = []

        if u'response' in cities_data:
            items = cities_data[u'response']['items']

        return json_response(items)


class VKGroupParser(View):
    def post(self, request, *args, **kwargs):
        code = 1
        gid = request.POST.get('gid', None)
        if gid:
            request.session['pgtid'] = sna.tasks.parse_group.delay(gid).id
            request.session['gid'] = gid
        else:
            code = 0
        return json_response(code)


class VKGroupParserChecker(View):
    def post(self, request, *args, **kwargs):
        tid = request.session.get('pgtid', None)
        if tid:
            result = app.AsyncResult(tid)
            return json_response(result.ready())
        return json_response(-1)


class VKGetParsedMembersCount(View):
    def post(self, request, *args, **kwargs):
        tid = request.session.get('pgtid', None)
        if tid:
            del request.session['pgtid']
            result = app.AsyncResult(tid)
            request.session['pgmftid'] = sna.tasks.parse_group_members_friends.delay(request.session['gid']).id
            return json_response(result.get())
        return json_response(-1)


class VKGroupMembersFriendsChecker(View):
    def post(self, request, *args, **kwargs):
        tid = request.session.get('pgmftid', None)
        if tid:
            result = app.AsyncResult(tid)
            return json_response(result.ready())
        return json_response(-1)