# coding=utf-8

"""
This module contains views
"""

from datetime import datetime
import os
from copy import deepcopy

import requests
from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from pymongo import MongoClient

from utils import json_response, get_access_token
from sna.celery import app
import sna.tasks


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
        get_access_token(request.session)
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
        'access_token': request.session.get('access_token'),
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
        'access_token': request.session.get('access_token')
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


def run_search_parser(request):
    """

    :param request:
    :return:
    """
    data = {
        'v': settings.API_VERSION,
        'access_token': request.session.get('access_token'),
        'count': 1000,
        'fields': 'photo_100'
    }

    country = request.POST.get('country_id')
    if country:
        data['country'] = country

    city = request.POST.get('city_id')
    if city:
        data['city'] = city

    sex = request.POST.get('sex')
    if sex:
        data['sex'] = sex

    age_from = request.POST.get('age_from')
    if age_from:
        data['age_from'] = age_from

    age_to = request.POST.get('age_to')
    if age_to:
        data['age_to'] = age_to

    print data

    r = requests.post(url=settings.SEARCH_URL, data=data)
    response = r.json()[u'response']

    return json_response(response)


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

        request.session['tid'] = sna.tasks.parse_group.delay(gid, request.session.get('access_token')).id
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
        request.session['tid'] = sna.tasks.parse_group_members_friends.delay(request.session['gid'],
                                                                             request.session.get('access_token')).id
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
        'access_token': request.session.get('access_token'),
        'user_ids': ids,
        'fields': 'photo_100,can_write_private_message,bdate,maiden_name,'
                  'can_post,about,wall_comments,'
                  'connections,relation,relatives,contacts'
    }

    r = requests.post(settings.GET_USER_URL, data=data)
    response = r.json()

    data = {
        'v': settings.API_VERSION,
        'group_id': request.session.get('gid'),
        'access_token': request.session.get('access_token')
    }

    rsp = requests.post(settings.GET_GROUP_INFO_URL, data=data).json()

    if u'response' in response:
        response[u'response'][0]['group_name'] = rsp[u'response'][0]['name']
        rsp = deepcopy(response[u'response'])
        client = MongoClient()
        db = client[gid]
        targets = db['targets']
        targets.remove()
        targets.insert(response[u'response'])
        return json_response(rsp)

    return json_response(None)


def send_notification(request):
    """

    :param request:
    :return:
    """
    if 'ids' not in request.POST:
        return json_response(-1)

    ids = request.POST.get('ids')
    rd = settings.REQUEST_DATA.copy()
    rd['user_ids'] = ids
    rd['message'] = str(datetime.now())[:-7] + "\nТест для отправки сообщений"
    rd['access_token'] = request.session.get('access_token')
    requests.post(settings.SEND_MESSAGE_URL, data=rd)

    del rd['user_ids']

    gid = request.session.get('gid')
    ids = map(int, ids.split(','))
    client = MongoClient()
    db = client[gid]
    targets_c = db['targets']

    targets = targets_c.find({"id": {"$in": ids}})
    for t in targets:
        rd['message'] = str(datetime.now())[:-7] + "\n" + get_recommendations(t)
        rd['user_id'] = t['id']
        requests.post(settings.SEND_MESSAGE_URL, data=rd)

    return json_response(1)


def get_recommendations(user):
    """

    :param user:
    :return:
    """
    recommendation = "Мы рекомендуем:\n"
    rn = 0

    if u'wall_comments' in user and user[u'wall_comments']:
        rn += 1
        recommendation += str(rn) + ". Отключите возможность оставлять комментарии на вашей стене\n"

    if u'can_post' in user and user['can_post'] == 1:
        rn += 1
        recommendation += str(rn) + ". Отключите возможность оставлять записи на стене другим пользователям\n"

    if u'home_phone' in user and user[u'home_phone']:
        rn += 1
        recommendation += str(rn) + ". Скройте номер вашего домашнего телефона\n"

    if u'mobile_phone' in user and user[u'mobile_phone']:
        rn += 1
        recommendation += str(rn) + ". Скройте номер вашего мобильного телефона\n"

    return recommendation