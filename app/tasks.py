from __future__ import absolute_import, unicode_literals
from app.celery import app
import shutil
from core.tasks import async_send_update_error_mail
from rest_framework_simplejwt.token_blacklist.management.commands import flushexpiredtokens
from django.core import cache
from core.utils.cache import create_async_cache_workers
import celery
from app.mailer import send_new_user_email, send_new_user_request_email, send_bug_report_email
from users.models import CustomUser, UserRequest
from core.models import BugReport
from django.db import connection


@app.task(queue='celery')
def add(x, y):
    print(x + y)
    return x + y


@app.task(bind=True)
def shutdown(self):
    # Add shutdown task to queue to shutdown workers / restart after all tasks done
    app.control.revoke(self.id)  # prevent this task from being executed again
    app.control.shutdown()  # send shutdown signal to all workers


@app.task(bind=True, queue='celery', max_retries=0)
def sanity_check():
    logger.debug('Sanity check running.')


@app.task(bind=True, queue='celery', default_retry_delay=60, max_retries=1)
def clean_temp_directory():
    try:
        flushexpiredtokens.Command().handle()
        shutil.rmtree(settings.MEDIA_TEMP_ROOT)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, queue='celery', default_retry_delay=60, max_retries=1)
def reset_cache():
    try:
        cache.clear()
        create_async_cache_workers()
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, queue='celery', default_retry_delay=60, max_retries=1)
def clean_database():
    try:
        force_proxy = connection.cursor()
        realconn = connection.connection
        old_isolation_level = realconn.isolation_level
        realconn.set_isolation_level(0)
        cursor = realconn.cursor()
        cursor.execute('VACUUM ANALYZE')
        cursor.execute('REINDEX DATABASE anhd')
        realconn.set_isolation_level(old_isolation_level)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_new_user_email(self, user_id):
    user = CustomUser.objects.get(id=user_id)
    return send_new_user_email(user=user)


@app.task(bind=True, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_new_user_request_email(self, user_request_id):
    user_request = UserRequest.objects.get(id=user_request_id)
    return send_new_user_request_email(user_request=user_request)


@app.task(bind=True, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_bug_report_email(self, bug_report_id):
    bug_report = BugReport.objects.get(id=bug_report_id)
    return send_bug_report_email(bug_report=bug_report)
