# coding=utf-8
import urllib
import urllib2

from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext

from utils import json_response


class Index(View):
    def get(self, request, *args, **kwargs):

        countries = {
            '1': 'Россия',
            '2': 'Украина'
        }

        return render_to_response("index.html", {"countries": countries},
                                  RequestContext(request))


class VKSearch(View):
    def post(self, request, *args, **kwargs):
        country = int(request.POST.get('country', 0))
        if country == 0:
            return 0

        url = 'https://vk.com/select_ajax.php'
        data = {
            'act': 'a_get_country_info',
            'fields': 1,
            'country': country
        }
        headers = {
            'x-requested-with': 'XMLHttpRequest'
        }

        data = urllib.urlencode(data)
        vk_request = urllib2.Request(url, data, headers)
        vk_response = urllib2.urlopen(vk_request)
        data = vk_response.read().decode('cp1251')
        data = eval(data.replace('<b>', '').replace('<\\/b>', ''))
        return json_response(data['cities'])