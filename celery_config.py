# -*- coding: utf-8 -*-
#!/usr/bin/env python

from __future__ import absolute_import

from celery import platforms
from datetime import timedelta

platforms.C_FORCE_ROOT = True
broker_url = 'amqp://guest:guest@localhost:5672//'
result_backend = 'amqp://guest:guest@localhost:5672//'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
#timezone = 'Europe/Oslo'
enable_utc = True
task_result_expires = 3600

INSTALLED_APPS = ['cdsoss.tasks.task',]

CELERYBEAT_SCHEDULE = {
    # Executes every Monday morning at 7:30 A.M
    #'add-every-monday-morning': {
    #    'task': 'tasks.add',
    #    'schedule': crontab(hour=7, minute=30, day_of_week=1),
    #    'args': (16, 16),
    #},
    #'sync_images': {
    #'task': 'cdsoss.tasks.task.sync_images',
    #'schedule': timedelta(seconds=600),
    #'args': ()
    #},
    #'sync_vm_status': {
    #'task': 'cdsoss.tasks.task.sync_vm_status',
    #'schedule': timedelta(seconds=60),
    #'args': ()
    #},

}
