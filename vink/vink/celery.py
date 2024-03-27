# from __future__ import absolute_import

import os
import time

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vink.settings")

app = Celery("vink")
app.config_from_object("django.conf:settings", namespace="CELERY")
# app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()


@app.task()
def debug_task():
    time.sleep(20)
    print("Привет из debug_task")
