# coding=utf-8

from __future__ import absolute_import

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sna.settings')

from celery import Celery

app = Celery('sna',broker='amqp://',
             backend='amqp://', include=['sna.tasks'])

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')


app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)

if __name__ == '__main__':
    app.start()