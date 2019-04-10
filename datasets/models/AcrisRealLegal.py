from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from django.conf import settings

import os
import csv
import uuid
import logging
logger = logging.getLogger('app')


class AcrisRealLegal(BaseDatasetModel, models.Model):
    download_endpoint = 'https://data.cityofnewyork.us/api/views/8h5j-fqxa/rows.csv?accessType=DOWNLOAD'

    class Meta:
        indexes = [
            models.Index(fields=['bbl', 'documentid']),
            models.Index(fields=['documentid', 'bbl']),

        ]

    key = models.TextField(primary_key=True, blank=False, null=False)
    documentid = models.ForeignKey('AcrisRealMaster', db_column='documentid', db_constraint=False,
                                   on_delete=models.SET_NULL, null=True, blank=True)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    recordtype = models.TextField(blank=True, null=True)
    borough = models.SmallIntegerField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    easement = models.BooleanField(blank=True, null=True)
    partiallot = models.TextField(blank=True, null=True)
    airrights = models.BooleanField(blank=True, null=True)
    subterraneanrights = models.BooleanField(blank=True, null=True)
    propertytype = models.TextField(blank=True, null=True)
    streetnumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    goodthroughdate = models.DateTimeField(blank=True, null=True)

    slim_query_fields = ["bbl", "documentid"]

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['documentid']):
                continue
            if 'bbl' in row:  # why?
                row['bbl'] = str(row['bbl'])
            row['key'] = "{}-{}".format(row['documentid'], row['bbl'])  # add primary key
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def create_unique_csv(self, file_path):
        cursor = 0
        count = 0

        # headers: ['header1', 'header2',...]
        temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(
            'set_diff' + uuid.uuid4().hex) + '.mock' if settings.TESTING else '.csv')

        new_file = open(file_path, 'r')
        headers = new_file.readline().replace('\n', '').split(',')
        """Read csv file, delete duplicates and write it."""
        with open(file_path, 'r', newline='') as inputfile:
            with open(temp_file_path, 'w', newline='') as outputfile:
                duplicatereader = csv.DictReader(inputfile, delimiter=',', quotechar='"', doublequote=True,
                                                 quoting=csv.QUOTE_ALL, skipinitialspace=True)
                uniquewrite = csv.DictWriter(outputfile, fieldnames=headers, delimiter=',', quotechar='"', doublequote=True,
                                             quoting=csv.QUOTE_ALL, skipinitialspace=True)
                uniquewrite.writeheader()
                keysread = []
                for row in duplicatereader:
                    cursor = cursor + 1
                    key = (row['DOCUMENT ID'], row['BOROUGH'], row['BLOCK'], row['LOT'])
                    if key not in keysread:
                        count = count + 1
                        keysread.append(key)
                        uniquewrite.writerow(row)
                    else:
                        print("Dup: {}", key)
                    if cursor % settings.BATCH_SIZE == 0:
                        logger.debug('Cursor: {}, count: {}'.format(cursor, count))
        return temp_file_path

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), allow_blank=True))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        kwargs['file_path'] = self.create_unique_csv(kwargs['file_path'])
        return self.bulk_seed(raw=False, **kwargs)  # need to add the bbl, can't do raw
        # logger.debug("Seeding/Updating {}", self.__name__)
        # return self.seed_with_single(**kwargs)

    def __str__(self):
        return self.key
