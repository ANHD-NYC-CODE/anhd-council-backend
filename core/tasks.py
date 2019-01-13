from __future__ import absolute_import, unicode_literals
from app.celery import app
from core.models import Dataset, Update, DataFile
from django_celery_results.models import TaskResult

# TODO - setup auth for flower
# https://stackoverflow.com/questions/19689510/celery-flower-security-in-production

import logging

logger = logging.getLogger('app')


@app.task(bind=True)
def async_seed_file(self, dataset_id, file_id, update_id):
    dataset = Dataset.objects.get(id=dataset_id)
    file = DataFile.objects.get(id=file_id)
    update = Update.objects.get(id=update_id)

    logger.info("Beginning async seeding - {} - Update: {}".format(dataset.name, update.id))
    dataset.seed_dataset(file=file, update=update)


@app.task(bind=True)
def async_download_start(self, dataset_id):
    dataset = Dataset.objects.filter(id=dataset_id).first()
    logger.info("Starting async download for dataset: {}".format(dataset.name))
    if dataset:
        dataset.download()
    else:
        logger.error("*ERROR* - Task Failure - No dataset found in async_download_start")
        raise Exception("No dataset.")


@app.task(bind=True)
def async_download_and_update(self, dataset_id):
    dataset = Dataset.objects.filter(id=dataset_id).first()
    logger.info("Starting async download and update for dataset: {}".format(dataset.name))
    if dataset:
        dataset.download_and_update()
    else:
        logger.error("*ERROR* - Task Failure - No dataset found in async_download_start")
        raise Exception("No dataset.")
