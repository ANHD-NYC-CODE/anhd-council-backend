from __future__ import absolute_import, unicode_literals
from app.celery import app
from django_celery_results.models import TaskResult
from datasets import models as dataset_models


@app.task(bind=True)
def async_download_file(self, model_name, endpoint):
    return getattr(dataset_models, model_name).download_file(endpoint)
