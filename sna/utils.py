# coding=utf-8
import json
from django.http import HttpResponse


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