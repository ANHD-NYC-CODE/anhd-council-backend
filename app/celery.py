from __future__ import absolute_import, unicode_literals
import os
import sys
from celery import Celery
from celery.signals import worker_init
from django.utils import timezone
from celery.schedules import crontab


from django.conf import settings
import logging
logger = logging.getLogger('app')

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")

app = Celery('app', include=['app.tasks'])


# app.now = timezone.now
# Load task modules from all registered Django app configs.
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


from django.apps import apps
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
