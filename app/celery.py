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
             backend=settings.CELERY_BACKEND, include=['app.tasks', 'core.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')

# app.now = timezone.now
# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
