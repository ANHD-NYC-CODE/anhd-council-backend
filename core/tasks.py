from __future__ import absolute_import, unicode_literals
from app.celery import app
from core import models as c
from django_celery_results.models import TaskResult
from django.conf import settings
from app.mailer import send_update_error_mail

import os
# TODO - setup auth for flower
# https://stackoverflow.com/questions/19689510/celery-flower-security-in-production

import logging

logger = logging.getLogger('app')


@app.task(bind=True, queue='update')
def async_seed_file(self, file_path, update_id):
    try:
        update = c.Update.objects.get(id=update_id)
        file_path = os.path.join(settings.MEDIA_ROOT, os.path.basename(file_path))
        logger.info("Beginning async seeding - {} - c.Update: {}".format(update.file.dataset.name, update.id))
        update.file.dataset.seed_dataset(file_path=file_path, update=update)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        send_update_error_mail(e)


@app.task(bind=True, queue='update')
def async_seed_table(self, update_id):
    try:
        update = c.Update.objects.get(id=update_id)
        logger.info("Beginning async seeding - {} - c.Update: {}".format(update.dataset.name, update.id))
        update.dataset.seed_dataset(update=update)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        send_update_error_mail(e)


@app.task(bind=True, queue='celery')
def async_download_start(self, dataset_id):
    try:
        dataset = c.Dataset.objects.filter(id=dataset_id).first()
        logger.info("Starting async download for dataset: {}".format(dataset.name))
        if dataset:
            raise Exception("test error")
            dataset.download()
        else:
            logger.error("*ERROR* - Task Failure - No dataset found in async_download_start")
            raise Exception("No dataset.")
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        send_update_error_mail(e)


@app.task(bind=True, queue='update')
def async_download_and_update(self, dataset_id):
    try:
        dataset = c.Dataset.objects.filter(id=dataset_id).first()
        logger.info("Starting async download and update for dataset: {}".format(dataset.name))
        if dataset:
            dataset.download_and_update()
        else:
            logger.error("*ERROR* - Task Failure - No dataset found in async_download_start")
            raise Exception("No dataset.")
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        send_update_error_mail(e)
