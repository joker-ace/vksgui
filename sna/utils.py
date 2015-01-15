# coding=utf-8
import json
import os
import datetime

from django.http import HttpResponse
from django.conf import settings
from grab import Grab


def json_response(data=None):
    return HttpResponse(json.dumps(data), content_type="application/json")


def create_chunk(iterable, chunk_size=3):
    for i in xrange(0, len(iterable), chunk_size):
        yield iterable[i:i + chunk_size]


def create_execute_code(ids):
    template = '"{0}":API.friends.get({{"user_id":"{0}"}}).items'
    code = "return {"
    code += ','.join(template.format(_id) for _id in ids)
    code += "};"
    return code


def get_access_token(session):
    """

    :return:
    """

    token = session.get('access_token')
    if token:
        end_time = session['token_valid_date']
        date_format = '%Y-%m-%d %H:%M:%S'
        token_valid_date = datetime.datetime.strptime(end_time, date_format)
        now = datetime.datetime.now()
        seconds = (token_valid_date - now).seconds
        if seconds > 0:
            return

    need_auth = False
    if not os.path.exists(settings.GRAB_COOKIES_FILE):
        need_auth = True
        with open(settings.GRAB_COOKIES_FILE, 'w'):
            pass

    g = Grab(cookiefile=settings.GRAB_COOKIES_FILE)
    g.go(settings.TOKEN_REQUEST_URL)

    if need_auth:
        g.set_input('email', settings.VK_USER_EMAIL)
        g.set_input('pass', settings.VK_USER_PASSW)
        g.submit()

    start_token = 'Location:'

    start = g.response.head.rfind(start_token)
    data = g.response.head[start + len(start_token) + 1:]
    end = data.find('\r\n')
    data = data[:end]

    start_token = 'access_token='

    start = data.find(start_token)
    data = data[start + len(start_token):]
    end = data.find('&')
    token = data[:end]

    today = datetime.datetime.now()
    token_valid_date = str(today + datetime.timedelta(days=1))
    token_valid_date = token_valid_date[:token_valid_date.find('.')]

    session['token_valid_date'] = token_valid_date
    session['access_token'] = token
