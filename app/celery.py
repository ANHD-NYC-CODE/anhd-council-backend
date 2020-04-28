from __future__ import absolute_import, unicode_literals
from django.db import connection
from django.apps import apps
import os
import sys
import celery
from celery.signals import worker_init
from django.utils import timezone
from celery.schedules import crontab


from django.conf import settings
import logging
logger = logging.getLogger('app')

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")

app = celery.Celery('app', include=['app.tasks'])


# app.now = timezone.now
# Load task modules from all registered Django app configs.
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# https://stackoverflow.com/questions/31504591/interfaceerror-connection-already-closed-using-django-celery-scrapy


class FaultTolerantTask(celery.Task):
    """ Implements after return hook to close the invalid connection.
    This way, django is forced to serve a new connection for the next
    task.
    """
    abstract = True

    def after_return(self, *args, **kwargs):
        connection.close()
