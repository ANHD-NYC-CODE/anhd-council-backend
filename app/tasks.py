from __future__ import absolute_import, unicode_literals
from app.celery import app
import shutil
from core.tasks import async_send_general_task_error_mail
from rest_framework_simplejwt.token_blacklist.management.commands import flushexpiredtokens
from django.core.cache import cache
from core.utils.cache import create_async_cache_workers
import celery
from app.mailer import send_new_user_email, send_new_user_request_email, send_user_message_email
from users.models import CustomUser, UserRequest
from core.models import UserMessage
from django.db import connection, transaction
from core import models as c
from django.conf import settings
from django_celery_results.models import TaskResult
from app.celery import FaultTolerantTask
import logging
import os

logger = logging.getLogger('app')


@app.task(bind=True, queue='celery', base=FaultTolerantTask)
def add(self, x, y):
    print(x + y)
    return x + y


@app.task(bind=True, base=FaultTolerantTask)
def shutdown(self):
    # Add shutdown task to queue to shutdown workers / restart after all tasks done
    app.control.revoke(self.id)  # prevent this task from being executed again
    app.control.shutdown()  # send shutdown signal to all workers


@app.task(bind=True, base=FaultTolerantTask, queue='celery', max_retries=0)
def sanity_check(self):
    logger.info('Sanity check running.')


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=60, max_retries=1)
def async_ensure_update_task_results(self):
    c.Update.ensure_update_task_results()


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=60, max_retries=1)
def clean_temp_directory(self):
    try:
        flushexpiredtokens.Command().handle()
        folder = settings.MEDIA_TEMP_ROOT
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e

# clears cache


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=60, max_retries=1)
def reset_cache(self, token):
    try:
        cache.clear()
        create_async_cache_workers(token)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e

# does not clear cache


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=60, max_retries=1)
def recache(self, token):
    try:
        create_async_cache_workers(token)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=60, max_retries=1)
def clean_database(self):
    try:
        with transaction.atomic():
            force_proxy = connection.cursor()
            realconn = connection.connection
            old_isolation_level = realconn.isolation_level
            realconn.set_isolation_level(0)
            cursor = realconn.cursor()
            cursor.execute('VACUUM ANALYZE')
            cursor.execute('REINDEX DATABASE anhd')
            realconn.set_isolation_level(old_isolation_level)
            connection.close()
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_new_user_email(self, user_id):
    user = CustomUser.objects.get(id=user_id)
    return send_new_user_email(user=user)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_new_user_request_email(self, user_request_id):
    user_request = UserRequest.objects.get(id=user_request_id)
    return send_new_user_request_email(user_request=user_request)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_user_message_email(self, bug_report_id):
    bug_report = UserMessage.objects.get(id=bug_report_id)
    return send_user_message_email(bug_report=bug_report)


@app.task(bind=True, queue='celery')
def async_test_rollbar(self):
    # should error when called and trigger a rollbar notification
    return test_rollbar_bad_variable
