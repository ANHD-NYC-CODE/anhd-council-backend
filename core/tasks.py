from __future__ import absolute_import, unicode_literals
import itertools
from app.celery import app
from core.utils.database import insert_rows
from core.models import Dataset, Update, Building
from django_celery_results.models import TaskResult

BATCH_SIZE = 1000


@app.task(bind=True)
def async_seed_file(self, dataset_id, file_path, update_id):
    dataset = Dataset.objects.get(id=dataset_id)
    update = Update.objects.get(id=update_id)

    rows = dataset.transform_dataset(file_path)
    while True:
        batch = list(itertools.islice(rows, 0, BATCH_SIZE))
        if len(batch) == 0:
            break
        else:
            insert_rows(batch, eval(dataset.model_name)._meta.db_table, update)
