from django.db import models
from django.dispatch import receiver
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils.validation_filters import is_null
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
import pandas
import numpy
import csv
from datetime import datetime
from core.utils.database import execute
from core.tasks import async_download_and_update
from datasets import models as ds

import logging
logger = logging.getLogger('app')


class OCAHousingCourt(BaseDatasetModel, models.Model):
    QUERY_DATE_KEY = 'fileddate'
    # RECENT_DATE_PINNED = True
    REQUIRES_AUTHENTICATION = True


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

    court = models.TextField(blank=True, null=True)
    fileddate = models.DateField(blank=True, null=True)
    propertytype = models.TextField(blank=True, null=True)
    classification = models.TextField(blank=True, null=True)
    specialtydesignationtypes = models.TextField(blank=True, null=True)
    disposeddate = models.DateField(blank=True, null=True)
    disposedreason = models.TextField(blank=True, null=True)
    firstpaper = models.TextField(blank=True, null=True)
    primaryclaimtotal = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    dateofjurydemand = models.TextField(blank=True, null=True)
    bct2020 = models.CharField(max_length=25, blank=True, null=True)
    bctcb2020 = models.CharField(max_length=25, blank=True, null=True)
    ct2010 = models.CharField(max_length=25, blank=True, null=True)
    cb2010 = models.CharField(max_length=25, blank=True, null=True)

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

            # Create Tempfile for OCA with addresses and oca index
            oca_base_tf = tempfile.NamedTemporaryFile()
            logger.info("Download started for: {} at aws".format(
                dataset.name))
            client.download_fileobj(AWS_BUCKET_NAME, 'oca_addresses_with_bbl.csv', oca_base_tf)

            oca_index_tf = tempfile.NamedTemporaryFile()
            logger.info("Download started for: oca index at aws")
            client.download_fileobj(AWS_BUCKET_NAME, 'oca_index.csv', oca_index_tf)
        except Exception as e:
            logger.error(
                "* ERROR * AWS OCA download failed")
            raise e

        try:
            oca_base_file = open(oca_base_tf.name, newline='')
            oca_index_file = open(oca_index_tf.name, newline='')

            # Create oca joined temp file
            oca_joined_tf = tempfile.NamedTemporaryFile()
            oca_joined_file = open(oca_joined_tf.name, 'w', newline='')

            oca_index_frame = pandas.read_csv(oca_index_file.name)
            oca_index = oca_index_frame.set_index('indexnumberid')
            oca_index.sort_values(['indexnumberid'],
                    axis=0,
                    ascending=[True],
                    inplace=True)

            oca_base = csv.reader(oca_base_file, delimiter=',', quotechar='"')
            print('test')
            oca_joined = csv.writer(oca_joined_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

            base_header = oca_base.__next__()
            index_header = oca_index_file.readline().replace('\n', '').split(',')[1:]
            oca_index_file.close()

            # Write headers and joined csv
            oca_joined.writerow(base_header + index_header)

            for base_row in oca_base:
                indexnumberid = base_row[0]

                # Skip if no bbl
                if base_row[15] == '':
                    continue

                try:
                    oca_index_row = oca_index.loc[indexnumberid].tolist()
                except KeyError:
                    logger.error("indexnumber id {} not found".format(indexnumberid))
                    continue

                # Remove spaces from classification (3) and status (5)
                oca_index_row[3] = oca_index_row[3].replace(' ', '-')
                oca_index_row[5] = oca_index_row[5].replace(' ', '-')

                for index, item in enumerate(oca_index_row):
                    if type(item) == numpy.float64 or type(item) == float:
                        oca_index_row[index] = str(item) if str(item) != 'nan' else ''
                    else:
                        oca_index_row[index] = str(item)

                oca_joined.writerow(base_row + oca_index_row)
        except Exception as e:
            logger.error(
                "* ERROR * AWS OCA join failed {}".format(e))
            raise e

        oca_joined_file.close()
        # oca_joined_file = open(oca_joined_tf.name, newline='')
        data_file = c_models.DataFile(dataset=dataset)
        data_file.file.save('oca_joined.csv', files.File(oca_joined_tf))
        logger.info("Download and join completed for: {} and saved to: {}".format(
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

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_standard()

    def __str__(self):
        return str(self.indexnumberid)
