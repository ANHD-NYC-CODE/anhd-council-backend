from __future__ import absolute_import, unicode_literals
from app.celery import app
from core.utils.database import seed_generator_rows
from core.models import Dataset, Update, DataFile
from django_celery_results.models import TaskResult


@app.task(bind=True)
def async_seed_generator_rows(self, dataset_id, file_id, update_id):
    dataset = Dataset.objects.get(id=dataset_id)
    file = DataFile.objects.get(id=file_id)
    update = Update.objects.get(id=update_id)
    rows = dataset.transform_dataset(file.file.path)

    seed_generator_rows(dataset.model_name, rows, update)


@app.task(bind=True)
def async_download_file(self):
    print("******")
