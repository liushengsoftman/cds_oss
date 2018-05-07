# -*- coding: utf-8 -*-
#!/usr/bin/env python

from __future__ import absolute_import

from celery import Celery
from cdsoss import celery_config

app = Celery('cdsoss')

app.config_from_object(celery_config)
app.autodiscover_tasks(lambda: celery_config.INSTALLED_APPS)

if __name__ == '__main__':
    app.start()