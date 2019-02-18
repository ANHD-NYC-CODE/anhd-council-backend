from __future__ import absolute_import, unicode_literals
from app.celery import app
import shutil
from core.tasks import async_send_update_error_mail
from rest_framework_simplejwt.token_blacklist.management.commands import flushexpiredtokens
from django.core import cache
import celery


@app.task(queue='celery')
def add(x, y):
    print(x + y)
    return x + y


@app.task(bind=True)
def shutdown(self):
    # Add shutdown task to queue to shutdown workers / restart after all tasks done
    app.control.revoke(self.id)  # prevent this task from being executed again
    app.control.shutdown()  # send shutdown signal to all workers


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
def clear_cache():
    try:
        cache.clear()
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e
