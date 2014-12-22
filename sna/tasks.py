# coding=utf-8
from __future__ import absolute_import
import os
import time
from threading import Thread

import requests
from django.conf import settings
import pymongo
import networkx as nx

from sna.celery import app
from sna.utils import create_chunk, create_execute_code
from attaks.attacks import attack


@app.task
def parse_group(gid, access_token):
    """

    :param gid:
    :return:
    """
    path = os.path.join(settings.MEMBERS_FILES_DIR, '{}.members'.format(str(gid)))
    rd = settings.REQUEST_DATA.copy()

    rd['group_id'] = str(gid)
    rd['sort'] = 'id_asc'
    rd['access_token'] = access_token
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
                        line = ','.join(map(str, response['items'])) + '\n'
                        if line != '\n':
                            fptr.write(line)
                    rd['offset'] += 1000
                except KeyError:
                    pass
            time.sleep(1)

    return count


def parse_group_members_friends_routine(rd, gid):
    """

    :param rd:
    :param gid:
    :return:
    """
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
        except Exception:
            print rd
            try:
                print response.content
            except:
                print response

            print 'Retry in 1 second'
            time.sleep(0.7)


@app.task
def parse_group_members_friends(gid, access_token):
    """

    :param gid:
    :return:
    """
    members = list()
    path = os.path.join(settings.MEMBERS_FILES_DIR, '{}.members'.format(str(gid)))
    with open(path) as f:
        for line in f:
            if line != '\n':
                members.extend(line.strip().split(','))

    rd = settings.REQUEST_DATA.copy()
    rd['access_token'] = access_token
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
        time.sleep(0.5)


def find_common_friends(gid, uids):
    """

    :param gid:
    :param uids:
    :return:
    """
    client = pymongo.MongoClient()
    db = client[gid]
    friends_c = db['friends']
    common_friends_c = db['common_friends']
    chunk = list()
    for member in uids:
        results = friends_c.find({'friends': {'$in': [int(member)]}})
        mcf = dict(uid=member, friends=list())
        for m in results:
            mcf['friends'].append(m['uid'])
        chunk.append(mcf)

    common_friends_c.insert(chunk)


@app.task
def parse_members_relations(gid):
    """

    :param gid:
    :return:
    """
    members = list()
    path = os.path.join(settings.MEMBERS_FILES_DIR, '{}.members'.format(str(gid)))
    with open(path) as f:
        for line in f:
            if line != '\n':
                members.extend(line.strip().split(','))
    threads = []
    for chunk in create_chunk(members, 200):
        for uids in create_chunk(chunk, 50):
            t = Thread(target=find_common_friends, args=(gid, uids))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    client = pymongo.MongoClient()
    db = client[gid]
    common_friends_c = db['common_friends']
    path = os.path.join(settings.MEMBERS_FILES_DIR, '{}_common_friends.txt'.format(str(gid)))
    with open(path, 'w') as outf:
        for member in common_friends_c.find({}, {'_uid': 0}):
            line = (str(member['uid']) + " " + ' '.join(map(str, member['friends']))).strip() + '\n'
            outf.write(line)


def printTargets(percTreshold, listOfTargets, gid):
    i = 0
    path = os.path.join(settings.MEMBERS_FILES_DIR, '{}_targets.txt'.format(gid))
    with open(path, 'w') as fdWrite:
        while i < int(len(listOfTargets) * percTreshold):
            fdWrite.write("{}\n".format(listOfTargets[i]))
            i += 1

@app.task
def start_percolation_attack(gid):
    """

    :param gid:
    :return:
    """
    path = os.path.join(settings.MEMBERS_FILES_DIR, '{}_common_friends.txt'.format(gid))
    graph = nx.read_adjlist(path, delimiter=' ')
    attack(graph, 'target')
    results = attack(graph, 'target')
    printTargets(results[1], results[6], gid)