from __future__ import absolute_import, unicode_literals
from app.celery import app
from core.models import Dataset, Update, DataFile
from django_celery_results.models import TaskResult

from django.core import files
# TODO - setup auth for flower
# https://stackoverflow.com/questions/19689510/celery-flower-security-in-production


@app.task(bind=True)
def async_seed_file(self, dataset_id, file_id, update_id):
    dataset = Dataset.objects.get(id=dataset_id)
    file = DataFile.objects.get(id=file_id)
    update = Update.objects.get(id=update_id)

    dataset.seed_dataset(file=file, update=update)


@app.task(bind=True)
def async_download_start(self, dataset_id):
    dataset = Dataset.objects.filter(id=dataset_id).first()
    if dataset:
        dataset.download()
    else:
        raise Exception("No dataset.")
