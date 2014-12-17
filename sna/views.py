# coding=utf-8

"""
This module contains views
"""

import requests
from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from pymongo import MongoClient

from utils import json_response
from sna.celery import app
import sna.tasks

import os

class Index(View):
    """
    This is a view class for index page
    """
    template_name = "index.html"

    def get(self, request):
        """

        :param request:
        :return:
        """
        countries = {
            '1': 'Россия',
            '2': 'Украина'
        }

        return render_to_response(self.template_name, {"countries": countries},
                                  RequestContext(request))


def get_groups_by_query(request):
    """

    :param request:
    :return:
    """
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

    r = requests.post(settings.GET_GROUPS_URL, data=data)
    groups_data = r.json()
    if u'response' in groups_data:
        return json_response(groups_data[u'response']['items'])

    return json_response(0)


def get_cities_by_query(request):
    """

    :param request:
    :return:
    """
    cid = int(request.POST.get('country', 0))
    if cid == 0:
        return json_response(0)

    data = {
        'country_id': cid,
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


def run_group_parser(request):
    """

    :param request:
    :return:
    """

    code = 0
    gid = request.POST.get('gid', None)
    if gid:
        c = MongoClient()
        c[gid]['friends'].remove()
        c[gid]['common_friends'].remove()

        request.session['tid'] = sna.tasks.parse_group.delay(gid).id
        request.session['gid'] = gid
        code = 1

    return json_response(code)


def get_group_parsing_status(request):
    """

    :param request:
    :return:
    """
    tid = request.session.get('tid')
    if tid:
        return json_response(app.AsyncResult(tid).ready())
    return json_response(-1)


def get_group_members_count(request):
    """

    :param request:
    :return:
    """
    tid = request.session.get('tid')
    if tid:
        count = app.AsyncResult(tid).get()
        request.session['tid'] = sna.tasks.parse_group_members_friends.delay(request.session['gid']).id
        return json_response(count)
    return json_response(-1)


def get_friends_parsing_status(request):
    """

    :param request:
    :return:
    """
    tid = request.session.get('tid')
    if tid:
        status = app.AsyncResult(tid).ready()
        gid = request.session.get('gid')
        parsed = MongoClient()[gid]['friends'].count()
        return json_response(dict(ready=status, parsed=parsed))
    return json_response(-1)


def run_relations_search(request):
    """

    :param request:
    :return:
    """
    code = 0
    gid = request.session.get('gid')
    if gid:
        request.session['tid'] = sna.tasks.parse_members_relations.delay(gid).id
        code = 1

    return json_response(code)


def get_relations_search_status(request):
    """

    :param request:
    :return:
    """
    tid = request.session.get('tid')
    if tid:
        status = app.AsyncResult(tid).ready()
        gid = request.session.get('gid')
        parsed = MongoClient()[gid]['common_friends'].count()
        return json_response(dict(ready=status, parsed=parsed))
    return json_response(-1)


def run_attack(request):
    """

    :param request:
    :return:
    """
    code = 0
    gid = request.session.get('gid')
    if gid:
        request.session['tid'] = sna.tasks.start_percolation_attack.delay(gid).id
        code = 1
    return json_response(code)


def get_attack_status(request):
    """

    :param request:
    :return:
    """
    tid = request.session.get('tid')
    return json_response(app.AsyncResult(tid).ready())


def get_attack_results(request):
    """

    :param request:
    :return:
    """
    gid = request.session.get('gid')
    ids = list()
    if gid:
        path = os.path.join(settings.MEMBERS_FILES_DIR, '{}_targets.txt'.format(gid))
        with open(path) as inf:
            for id in inf:
                if id != '' or id != '\n':
                    ids.append(id)

    ids = ','.join(ids)

    data = {
        'v': settings.API_VERSION,
        'access_token': settings.VK_API_TOKEN,
        'user_ids': ids,
        'fields': 'photo_100'
    }

    r = requests.post(settings.GET_USER_URL, data=data)
    response = r.json()
    if u'response' in response:
        return json_response(response[u'response'])

    return json_response(None)