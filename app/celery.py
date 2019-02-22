from __future__ import absolute_import, unicode_literals
import os
import sys
from celery import Celery
from celery.signals import worker_init
from django.utils import timezone

from django.conf import settings
import logging
logger = logging.getLogger('app')

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")

app = Celery('app', broker=settings.CELERY_BROKER_URL,
             backend=settings.CELERY_BACKEND, include=['app.tasks'])


# Restart interrupted tasks with late_acks enabled
# https://gist.github.com/mlavin/6671079


# def restore_all_unacknowledged_messages():
#     conn = app.connection(transport_options={'visibility_timeout': 0})
#     qos = conn.channel().qos
#     qos.restore_visible()
#     logger.info('Unacknowledged messages restored')


# @worker_init.connect
# def configure(sender=None, conf=None, **kwargs):
#     restore_all_unacknowledged_messages()


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.broker_transport_options = {'visibility_timeout': 36000}  # 10 hours
# app.conf.update(
#     worker_pool_restarts=True,
# )

app.now = timezone.now
# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
