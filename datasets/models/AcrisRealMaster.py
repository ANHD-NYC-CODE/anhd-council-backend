from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets.utils import advanced_filter as af
from django.db.models import Q
from django.conf import settings
import os
import csv
import uuid
import logging

logger = logging.getLogger('app')


class AcrisRealMaster(BaseDatasetModel, models.Model):
    download_endpoint = 'https://data.cityofnewyork.us/api/views/bnx9-e6tj/rows.csv?accessType=DOWNLOAD'

    class Meta:
        indexes = [
            models.Index(fields=['documentid', 'doctype']),
            models.Index(fields=['doctype', 'documentid']),
            models.Index(fields=['documentid', 'docdate']),
            models.Index(fields=['docdate', 'documentid']),
            models.Index(fields=['documentid', 'docamount']),
            models.Index(fields=['docamount', 'documentid']),

        ]

    documentid = models.TextField(primary_key=True, blank=False, null=False)
    recordtype = models.TextField(blank=True, null=True)
    crfn = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    doctype = models.TextField(db_index=True, blank=True, null=True)
    docdate = models.DateTimeField(db_index=True, blank=True, null=True)
    docamount = models.BigIntegerField(db_index=True, blank=True, null=True)
    recordedfiled = models.DateTimeField(db_index=True, blank=True, null=True)
    modifieddate = models.DateTimeField(blank=True, null=True)
    reelyear = models.SmallIntegerField(blank=True, null=True)
    reelnbr = models.IntegerField(blank=True, null=True)
    reelpage = models.IntegerField(blank=True, null=True)
    pcttransferred = models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True)
    goodthroughdate = models.DateTimeField(blank=True, null=True)

    # https://data.cityofnewyork.us/City-Government/ACRIS-Document-Control-Codes/7isb-wh4c
    SALE_DOC_TYPES = ("DEED", "DEEDO", "DEED, LE", "DEED, RC", "DEED, TS", "DEEDP", "MTGE", "CORRM", "ASPM",
                      "AGMT", "SPRD", "AL&R", "M&CON")
    LEASE_DOC_TYPES = ("LEAS", "ASSTO", "MLEA1")

    TAX_DOC_TYPES = ("RPTT")

    @classmethod
    def construct_sales_query(self, relation_path):
        q_list = []
        for type in self.SALE_DOC_TYPES:
            q_list.append({'doctype': type})

        sales_filter = af.construct_or_q(q_list)

        return self.objects.filter(sales_filter).only('documentid')

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['documentid']):
                continue
            yield row
        return gen_rows

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_filters(self, gen_rows):
        for row in gen_rows:
            if row['docdate'] and is_older_than(row['docdate'], 1):
                continue
            yield row

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
                # headers = list(iter(next(duplicatereader)))
                uniquewrite = csv.DictWriter(outputfile, fieldnames=headers, delimiter=',', quotechar='"', doublequote=True,
                                             quoting=csv.QUOTE_ALL, skipinitialspace=True)
                uniquewrite.writeheader()
                keysread = []
                for row in duplicatereader:

                    cursor = cursor + 1
                    key = (row['DOCUMENT ID'],)
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
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        #
        # kwargs['file_path'] = self.create_unique_csv(kwargs['file_path'])
        # return self.bulk_seed(raw=True, **kwargs)
        return self.seed_with_single(**kwargs)

    def __str__(self):
        return self.documentid
