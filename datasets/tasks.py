from __future__ import absolute_import, unicode_literals
from app.celery import app
from django_celery_results.models import TaskResult
from datasets import models as dataset_models
import logging

logger = logging.getLogger(__name__)


@app.task(bind=True)
def async_download_file(self, model_name, endpoint):
    logger.info("Beginning Async Download - {} - {}".format(model_name, endpoint))
    return getattr(dataset_models, model_name).download_file(endpoint)
