from __future__ import absolute_import, unicode_literals
from app.celery import app
from core.models import Dataset, Update, DataFile
from django_celery_results.models import TaskResult

from django.core import files

import requests
import tempfile
import re

# TODO - setup auth for flower
# https://stackoverflow.com/questions/19689510/celery-flower-security-in-production


@app.task(bind=True)
def async_seed_file(self, dataset_id, file_id, update_id):
    dataset = Dataset.objects.get(id=dataset_id)
    file = DataFile.objects.get(id=file_id)
    update = Update.objects.get(id=update_id)

    dataset.seed_dataset(file=file, update=update)


@app.task(bind=True)
def async_download_file(self, dataset_id):
    dataset = Dataset.objects.filter(id=dataset_id).first()
    if dataset and dataset.download_endpoint:
        file_request = requests.get(dataset.download_endpoint, stream=True)
        # Was the request OK?
        if file_request.status_code != requests.codes.ok:
            # Nope, error handling, skip file etc etc etc
            raise Exception("Request error: {}".format(file_request.status_code))

        # get filename
        if 'content-disposition' in file_request.headers:
            file_name = re.findall("filename=(.+)", file_request.headers['content-disposition'])[0]
        else:
            file_name = dataset.download_endpoint.split('/')[-1]

        # Create a temporary file
        lf = tempfile.NamedTemporaryFile()

        # Read the streamed file in sections
        downloaded = 0
        for block in file_request.iter_content(1024 * 8):
            downloaded += len(block)
            print("{0} MB".format(downloaded / 1000000))
            # If no more file then stop
            if not block:
                break

            # Write file block to temporary file
            lf.write(block)

        data_file = DataFile(dataset=dataset)
        data_file.file.save(file_name, files.File(lf))
    else:
        raise Exception("No dataset or download endpoint.")
