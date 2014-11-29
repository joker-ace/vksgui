# coding=utf-8
import requests
import json

from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from utils import json_response


class Index(View):
    def get(self, request, *args, **kwargs):

        countries = {
            '1': 'Россия',
            '2': 'Украина'
        }

        return render_to_response("index.html", {"countries": countries},
                                  RequestContext(request))


class VKGetCities(View):
    def post(self, request, *args, **kwargs):
        countryId = int(request.POST.get('country', 0))
        if countryId == 0:
            return 0

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