from django.db import models
from django.db.models import Q
from django.core import files as dj_files
from core import models as c
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils.validation_filters import is_null, exceeds_char_length
from datasets.utils.pad_download import download_pad_bobaadr_csv, fetch_pad_last_updated
from core.utils.transform import from_csv_file_to_gen, with_bbl
from django.contrib.postgres.search import SearchVector, SearchVectorField
from core.tasks import async_create_update, async_download_and_update
from core.utils.address import clean_number_and_streets


import logging
from datasets import models as ds

logger = logging.getLogger('app')

# Update process: Automated (monthly via celerybeat) + manual CSV upload via admin
# Update strategy: Truncate + reload via bulk_seed(overwrite=True)
# Source: NYC Open Data Property Address Directory (bc8t-ecyu)
#
# The Socrata "download attachment" URL is stable across PAD releases — the file
# behind it changes (new ETag) but the URL doesn't. Download() pulls the ZIP,
# extracts bobaadr.txt, and saves it as bobaadr.csv (the file is already
# comma-separated with quoted values; only the extension needs swapping).
#
# Make sure to update the PADRecord dataset AFTER this one — it uses the same
# source file. Both are scheduled by celerybeat (see core/fixtures/tasks.yaml).

# NOTE on the BIN 1,000,000 error
# Currently the BIN field is the primary key field.
# However, it was discovered after building this table that NYC assigns "million" BINs to multiple buildings as a placeholder.
# see: https://nycplanning.github.io/Geosupport-UPG/chapters/chapterVI/section03/
# This results in missing buildings because the primary key field must be unique.
# Most missing addresses in the app are a result of this "million BIN" issue.
# TODO - migrate the primary key to a different value (perhaps a concatenation of BBL-BIN-LHND)
# Doing this will be tricky though, since you'll need to rework the API routing (currently is) /properties/<property PK>/buildings/<building PK>
# and make sure all the property > building associations stay intact


class Building(BaseDatasetModel, models.Model):
    # Socrata "download attachment" endpoint — redirects to a signed URL serving
    # the current PAD ZIP. New PAD releases change the file behind this URL
    # (new ETag); the URL itself is stable.
    download_endpoint = "https://data.cityofnewyork.us/download/bc8t-ecyu/application%2Fzip"

    bin = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', on_delete=models.SET_NULL, null=True,
                            db_column='bbl', db_constraint=False)
    boro = models.TextField(blank=False, null=False)
    block = models.TextField(blank=False, null=False)
    lot = models.TextField(blank=False, null=False)
    lhnd = models.TextField(blank=False, null=False)  # low house number
    lhns = models.TextField(blank=True, null=True)
    lcontpar = models.TextField(blank=True, null=True)
    lsos = models.TextField(blank=True, null=True)
    hhnd = models.TextField(blank=False, null=False)  # high house number
    hhns = models.TextField(blank=True, null=True)
    hcontpar = models.TextField(blank=True, null=True)
    hsos = models.TextField(blank=True, null=True)
    scboro = models.TextField(blank=True, null=True)
    sc5 = models.IntegerField(blank=True, null=True)
    sclgc = models.TextField(blank=True, null=True)
    stname = models.TextField(blank=True, null=True)
    addrtype = models.TextField(blank=True, null=True)
    realb7sc = models.TextField(blank=True, null=True)
    validlgcs = models.TextField(blank=True, null=True)
    dapsflag = models.TextField(blank=True, null=True)
    naubflag = models.TextField(blank=True, null=True)
    parity = models.TextField(blank=True, null=True)
    b10sc = models.BigIntegerField(blank=True, null=True)
    segid = models.IntegerField(blank=True, null=True)
    zipcode = models.IntegerField(blank=True, null=True)
    physicalid = models.IntegerField(blank=True, null=True)
    pad_addresses = models.TextField(default="", blank=True, null=True)

    def get_house_number(self):
        if (self.lhnd == self.hhnd):
            return self.lhnd
        elif (self.lhnd and self.hhnd):
            return "{}-{}".format(self.lhnd, self.hhnd)
        else:
            return self.lhnd

    @classmethod
    def construct_house_number(self, low, high):
        if (low == high):
            return low
        elif (low and high):
            return "{}-{}".format(low, high)
        else:
            return low

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['bin']):
                continue
            if is_null(row['lot']):
                continue
            if is_null(row['block']):
                continue
            if is_null(row['hhnd']):
                continue
            if is_null(row['lhnd']):
                continue
            row['stname'] = clean_number_and_streets(
                row['stname'], False, clean_typos=False)
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), borough='boro'))

    # PAD chain step 1 → 2. Declared as a class attribute so Dataset.seed_dataset
    # fires the chain trigger *after* all post-processing completes (instead of
    # from inside seed_or_update_self where it raced with the wrapping celery
    # task's tail and produced KeyError(None)).
    chain_next_model = 'PadRecord'

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        self.bulk_seed(**kwargs, overwrite=True)

    @classmethod
    def fetch_last_updated(cls):
        # Socrata `viewLastModified` — the real publish timestamp NYC bumps
        # when they push a new PAD release. See datasets/utils/pad_download.py.
        return fetch_pad_last_updated(cls.download_endpoint)

    @classmethod
    def download(cls, endpoint=None, file_name=None):
        # Downloads PAD ZIP, extracts bobaadr.txt, saves as bobaadr.csv DataFile.
        return download_pad_bobaadr_csv(
            dataset=cls.get_dataset(),
            url=endpoint or cls.download_endpoint,
        )

    @classmethod
    def create_async_update_worker(cls, endpoint=None, file_name=None):
        async_download_and_update.delay(
            cls.get_dataset().id, endpoint=endpoint, file_name=file_name)

    def __str__(self):
        return str(self.bin)
