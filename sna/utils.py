# coding=utf-8
import json
from django.http import HttpResponse
import requests
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


def get_access_token():
    g = Grab()
    g.go(settings.TOKEN_REQUEST_URL)
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
    data = data[:end]
    return data
