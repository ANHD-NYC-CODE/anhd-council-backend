from __future__ import absolute_import, unicode_literals
from app.celery import app
from core import models as c
from django_celery_results.models import TaskResult
from django.conf import settings
from app.mailer import send_update_error_mail, send_update_success_mail, send_general_task_error_mail

import os

import logging

logger = logging.getLogger('app')


@app.task(bind=True, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_general_task_error_mail(self, error):
    return send_general_task_error_mail(error)


@app.task(bind=True, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_update_error_mail(self, update_id, error):
    update = c.Update.objects.get(id=update_id)
    return send_update_error_mail(update, error)


@app.task(bind=True, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_update_success_mail(self, update_id):
    update = c.Update.objects.get(id=update_id)
    return send_update_success_mail(update)


@app.task(bind=True, queue='celery', acks_late=True, max_retries=1)
def async_create_update(self, dataset_id, file_id=None):
    file = c.DataFile.objects.get(id=file_id) if file_id else None
    try:
        dataset = c.Dataset.objects.filter(id=dataset_id).first()
        logger.info("Starting async download for dataset: {}".format(dataset.name))
        if dataset:
            dataset.update(file=file)
        else:
            logger.error("*ERROR* - Task Failure - No dataset found in async_download_start")
            raise Exception("No dataset.")
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, queue='update', acks_late=True, max_retries=1)
def async_seed_file(self, file_path, update_id, dataset_id=None):
    try:
        # manually set file and previous file in admin ui
        update = c.Update.objects.get(id=update_id)
        file_path = os.path.join(settings.MEDIA_ROOT, os.path.basename(file_path))
        dataset = c.Dataset.objects.get(id=dataset_id) if dataset_id else update.file.dataset
        logger.info("Beginning async seeding - {} - c.Update: {}".format(update.file.dataset.name, update.id))
        dataset.seed_dataset(file_path=file_path, update=update)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        if update:
            async_send_update_error_mail.delay(update.id, str(e))
        else:
            async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, queue='update', acks_late=True, max_retries=1)
def async_seed_table(self, update_id):
    try:
        update = c.Update.objects.get(id=update_id)
        logger.info("Beginning async seeding - {} - c.Update: {}".format(update.dataset.name, update.id))
        update.dataset.seed_dataset(update=update)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        if update:
            async_send_update_error_mail.delay(update.id, str(e))
        else:
            async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, queue='celery', acks_late=True, max_retries=1)
def async_download_start(self, dataset_id):
    try:
        dataset = c.Dataset.objects.filter(id=dataset_id).first()
        logger.info("Starting async download for dataset: {}".format(dataset.name))
        if dataset:
            dataset.download()
        else:
            logger.error("*ERROR* - Task Failure - No dataset found in async_download_start")
            raise Exception("No dataset.")
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, queue='celery', acks_late=True, max_retries=1)
def async_download_and_update(self, dataset_id):
    try:
        dataset = c.Dataset.objects.filter(id=dataset_id).first()
        logger.info("Starting async download and update for dataset: {}".format(dataset.name))
        if dataset:
            previous_file = dataset.latest_file()
            previous_file_id = previous_file.id if previous_file else None
            file = dataset.download()
            async_update_from_file.delay(file.id, previous_file_id)
            dataset.delete_old_files()
        else:
            logger.error("*ERROR* - Task Failure - No dataset found in async_download_start")
            raise Exception("No dataset.")
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, queue='update', acks_late=True, max_retries=1)
def async_update_from_file(self, file_id, previous_file_id):
    try:
        update = None
        file = c.DataFile.objects.get(id=file_id)
        previous_file = c.DataFile.objects.filter(id=previous_file_id).first()
        dataset = file.dataset
        logger.info("Starting async update for dataset: {}".format(dataset.name))
        update = c.Update.objects.create(dataset=dataset, file=file, previous_file=previous_file)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        if update:
            async_send_update_error_mail.delay(update.id, str(e))
        else:
            async_send_general_task_error_mail.delay(str(e))
        raise e
