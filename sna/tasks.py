# coding=utf-8
from __future__ import absolute_import
from sna.celery import app
import requests
import os
import time
from sna.utils import create_chunk, create_execute_code
from django.conf import settings
from threading import Thread
import pymongo

@app.task
def parse_group(gid):
    path = os.path.join(settings.MEMBERS_FILES_DIR, '{}.members'.format(str(gid)))
    rd = settings.REQUEST_DATA.copy()

    rd['group_id'] = str(gid)
    rd['sort'] = 'id_asc'
    response = requests.post(url=settings.GET_GROUP_MEMBERS_URL, data=rd)
    response = eval(response.content)['response']
    count = response['count']

    with open(path, 'w') as fptr:
        fptr.write(','.join(map(str, response['items'])) + '\n')

    if count > 1000:
        rd['offset'] = 1000
        while len(response['items']) > 0:
            for _ in xrange(3):
                try:
                    response = requests.post(url=settings.GET_GROUP_MEMBERS_URL, data=rd)
                    response = eval(response.content)['response']
                    with open(path, 'a') as fptr:
                        fptr.write(','.join(map(str, response['items'])) + '\n')
                    rd['offset'] += 1000
                except KeyError:
                    pass
            time.sleep(1)

    return count


def parse_group_members_friends_routine(rd, gid):
    client = pymongo.MongoClient()
    db = client[gid]
    friends_c = db['friends']
    while True:
        try:
            response = requests.post(url=settings.EXECUTE_URL, data=rd)
            response = response.json()['response']
            for member, friends_list in response.iteritems():
                if friends_list is None:
                    continue
                friends_c.insert(dict(uid=int(member), friends=friends_list))
            break
        except Exception as ex:
            print response.content
            print 'Retry in 1 second'
            time.sleep(0.7)


@app.task
def parse_group_members_friends(gid):
    members = list()
    path = os.path.join(settings.MEMBERS_FILES_DIR, '{}.members'.format(str(gid)))
    with open(path) as f:
        for line in f:
            members.extend(line.strip().split(','))

    rd = settings.REQUEST_DATA.copy()

    for chunk in create_chunk(members, chunk_size=75):
        processes = list()
        for ids in create_chunk(chunk, 25):
            code = create_execute_code(ids)
            rd['code'] = code
            p = Thread(target=parse_group_members_friends_routine, args=(rd.copy(), str(gid)))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()
        time.sleep(0.2)