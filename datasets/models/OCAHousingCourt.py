from django.db import models
from django.dispatch import receiver
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from core import models as c_models
from datasets.utils import dates
from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware
from django.core import files

import tempfile
import os
import boto3
from datetime import datetime
from core.utils.database import execute
from core.tasks import async_download_and_update
from datasets import models as ds

import logging
logger = logging.getLogger('app')


class OCAHousingCourt(BaseDatasetModel, models.Model):

    class Meta:
        indexes = [
        ]

    indexnumberid = models.TextField(primary_key=True, blank=False, null=False)
    street1 = models.TextField(default="", blank=True, null=True)
    street2 = models.TextField(default="", blank=True, null=True)
    city = models.TextField(default="", blank=True, null=True)
    state = models.TextField(default="", blank=True, null=True)
    postalcode = models.TextField(default="", blank=True, null=True)
    status = models.TextField(default="", blank=True, null=True)
    housenumber = models.TextField(default="", blank=True, null=True)
    streetname = models.TextField(default="", blank=True, null=True)
    sname = models.TextField(default="", blank=True, null=True)
    hnum = models.TextField(default="", blank=True, null=True)
    lat = models.TextField(default="", blank=True, null=True)
    lng = models.TextField(default="", blank=True, null=True)
    lon = models.TextField(default="", blank=True, null=True)
    boroughcode = models.TextField(default="", blank=True, null=True)
    placename = models.TextField(default="", blank=True, null=True)
    boro = models.TextField(default="", blank=True, null=True)
    cd = models.IntegerField(default=None, blank=True, null=True)
    ct = models.IntegerField(default=None, blank=True, null=True)
    council = models.IntegerField(default=None, blank=True, null=True)
    grc = models.IntegerField(default=None, blank=True, null=True)
    grc2 = models.IntegerField(default=None, blank=True, null=True)
    msg = models.TextField(default="", blank=True, null=True)
    msg2 = models.TextField(default="", blank=True, null=True)
    unitsres = models.IntegerField(default=None, blank=True, null=True)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)


    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        dataset = self.get_dataset()

        AWS_ACCESS_KEY = os.environ['OCA_AWS_ACCESS_KEY_ID']
        AWS_SECRET_KEY = os.environ['OCA_AWS_SECRET_ACCESS_KEY']
        AWS_BUCKET_NAME = os.environ['OCA_AWS_BUCKET_NAME']

        try:
            # Make AWS client for oca bucket
            client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
            )

            # Create Tempfile
            lf = tempfile.NamedTemporaryFile()
            logger.info("Download started for: {} at aws".format(
                dataset.name))
            client.download_fileobj(AWS_BUCKET_NAME, 'oca_addresses_with_bbl.csv', lf)
        except Exception as e:
            logger.error(
                "* ERROR * AWS OCA download failed")
            raise e

        data_file = c_models.DataFile(dataset=dataset)
        data_file.file.save('oca_addresses_with_bbl.csv', files.File(lf))
        logger.info("Download completed for: {} and saved to: {}".format(
            self.get_dataset().name, data_file.file.path))
        return data_file
        # return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating {}", self.__name__)
        self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.indexnumberid)
