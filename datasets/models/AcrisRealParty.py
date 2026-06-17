from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null

# ACRIS Real Party
# Links multiple party informations
# To single MasterLegal document by documentid
from django.conf import settings

import datetime
import os
import csv
import logging
from urllib.parse import urlencode
from core.tasks import async_download_and_update


logger = logging.getLogger('app')


class AcrisRealParty(BaseDatasetModel, models.Model):
    API_ID = '636b-3b5g'
    # Socrata /resource/ endpoint with SoQL :updated_at filter — see
    # AcrisRealMaster + AcrisRealLegal for the rationale. Party has no
    # docdate/modified_date columns (only good_through_date), so :updated_at
    # is the only available change-tracking column.
    base_download_endpoint = 'https://data.cityofnewyork.us/resource/636b-3b5g.csv'
    SOCRATA_LOOKBACK_DAYS = 120

    key = models.TextField(primary_key=True, blank=False, null=False)
    documentid = models.ForeignKey('AcrisRealMaster', db_column='documentid', db_constraint=False,
                                   on_delete=models.SET_NULL, null=True, blank=False)
    recordtype = models.TextField(blank=True, null=True)
    partytype = models.SmallIntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    goodthroughdate = models.DateField(blank=True, null=True)

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(cls, endpoint=None, file_name=None):
        if endpoint is None:
            endpoint = cls._build_socrata_url()
        logger.info("Downloading AcrisRealParty (filtered): %s", endpoint)
        return cls.download_file(endpoint, file_name=file_name)

    @classmethod
    def _build_socrata_url(cls):
        cutoff = (datetime.date.today() - datetime.timedelta(days=cls.SOCRATA_LOOKBACK_DAYS)).isoformat()
        # See AcrisRealMaster._build_socrata_url for the aliasing rationale.
        select = ','.join([
            'document_id AS documentid',
            'record_type AS recordtype',
            'party_type AS partytype',
            'name AS name',
            'address_1 AS address1',
            'address_2 AS address2',
            'country AS country',
            'city AS city',
            'state AS state',
            'zip AS zip',
            'good_through_date AS goodthroughdate',
        ])
        where = ":updated_at >= '{cutoff}'".format(cutoff=cutoff)
        query = urlencode({'$select': select, '$where': where, '$limit': 100000000})
        return '{}?{}'.format(cls.base_download_endpoint, query)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['documentid']):
                continue
            row['key'] = "{}-{}".format(row['documentid'],
                                        ''.join(e for e in row['name'] if e.isalnum()))
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def split_seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        return self.seed_with_single(delete_file=True, **kwargs)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        if settings.TESTING:
            return self.seed_with_single(**kwargs)
        else:
            return self.async_concurrent_seed(**kwargs)

    def __str__(self):
        return self.key
