from core import models as c_models
from core.utils.database import batch_upsert_from_gen, bulk_insert_from_file, seed_from_csv_diff
from core.utils.typecast import Typecast
from django.core import files
from core.utils.transform import foreign_key_formatting
from django.conf import settings

import os
import csv
import requests
import tempfile
import re
import logging

logger = logging.getLogger('app')


class BaseDatasetModel():
    @classmethod
    def get_dataset(self):
        return c_models.Dataset.objects.filter(model_name=self.__name__).first()

    @classmethod
    def download_file(self, endpoint):
        dataset = self.get_dataset()
        file_request = requests.get(endpoint, stream=True)
        # Was the request OK?
        if file_request.status_code != requests.codes.ok:
            # Nope, error handling, skip file etc etc etc
            logger.error("* ERROR * Download request failed: {}".format(endpoint))
            raise Exception("Request error: {}".format(file_request.status_code))

        # get filename
        if 'content-disposition' in file_request.headers:
            file_name = re.findall("filename=(.+)", file_request.headers['content-disposition'])[0]
        else:
            file_name = endpoint.split('/')[-1]

        # Create a temporary file
        lf = tempfile.NamedTemporaryFile()

        # Read the streamed file in sections
        downloaded = 0
        logger.info("Download started for: {} at {}".format(self.get_dataset().name, endpoint))

        for block in file_request.iter_content(1024 * 8):
            downloaded += len(block)
            logger.debug("{0} MB".format(downloaded / 1000000))
            # If no more file then stop
            if not block:
                break

            # Write file block to temporary file
            lf.write(block)
        data_file = c_models.DataFile(dataset=dataset)
        data_file.file.save(file_name, files.File(lf))
        logger.info("Download completed for: {} and saved to: {}".format(self.get_dataset().name, data_file.file.path))
        return data_file

    @classmethod
    def transform_self_from_file(self, file_path, update=None):
        return Typecast(self).cast_rows(foreign_key_formatting(self.transform_self(file_path, update)))

    @classmethod
    def seed_with_upsert(self, **kwargs):
        update = kwargs['update'] if 'update' in kwargs else None
        return batch_upsert_from_gen(self, self.transform_self_from_file(kwargs['file_path'], update=update), settings.BATCH_SIZE, update=update)

    @classmethod
    # Good for overwrites
    def bulk_seed(self, **kwargs):
        bulk_insert_from_file(self, **kwargs)

    @classmethod
    def seed_or_update_from_set_diff(self, **kwargs):
        new_file_path = kwargs['update'].file.file.path
        previous_file = kwargs['update'].previous_file

        if (previous_file and os.path.isfile(previous_file.file.path)):
            seed_from_csv_diff(previous_file.file.path, new_file_path, self, **kwargs)
        else:
            self.bulk_seed(**kwargs)
