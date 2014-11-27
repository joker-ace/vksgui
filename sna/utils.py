# coding=utf-8
import json
from django.http import HttpResponse

def json_response(data):
    return HttpResponse(json.dumps(data), content_type="application/json")