from django.db import connection, models, transaction
from django.db.models import Q
from core import models as c
from datasets import models as ds
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils.validation_filters import is_null, exceeds_char_length
from datasets.utils.pad_download import download_pad_bobaadr_csv, fetch_pad_last_updated
from core.utils.transform import from_csv_file_to_gen, with_bbl
from django.contrib.postgres.search import SearchVector, SearchVectorField
from core.tasks import async_create_update, async_download_and_update
from core.utils.address import clean_number_and_streets
from django.conf import settings
import re
import logging

logger = logging.getLogger('app')

# Update process: Automated (monthly via celerybeat) + manual CSV upload via admin
# Update strategy: Truncate + reload via bulk_seed(overwrite=True, ignore_conflict=True),
# followed by annotate_buildings() which fills Building.pad_addresses.
# Source: NYC Open Data Property Address Directory (bc8t-ecyu) — same file as
# Building (bobaadr.txt extracted from the PAD ZIP). Each model independently
# downloads + extracts; the cost is two 46 MB pulls per cron tick, which is
# cheaper than the coordination cost of sharing one download.
#
# Schedule this AFTER Building on the same cron tick — annotate_buildings() reads
# Building rows to attach PAD addresses, so Building should already be current.


class PadRecord(BaseDatasetModel, models.Model):
    # Socrata "download attachment" endpoint — same as Building. New PAD
    # releases change the file behind this URL; the URL itself is stable.
    download_endpoint = "https://data.cityofnewyork.us/download/bc8t-ecyu/application%2Fzip"

    key = models.TextField(primary_key=True, blank=False, null=False)
    bin = models.ForeignKey('Building', on_delete=models.SET_NULL, null=True,
                            db_column='bin', db_constraint=False)
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
            row['key'] = re.sub(
                ' ', '', "{}{}-{}{}".format(row['bin'], row['lhnd'], row['hhnd'], row['stname']))
            yield row

    @classmethod
    def annotate_buildings(self):
        # SQL-level aggregation. Previously this method iterated every Building
        # (~1.1M rows) in a Python loop, fired one SELECT per row to fetch
        # matching PadRecords, then `building.save()` per match — roughly 2.2M
        # DB round-trips, ~20+ minutes in practice. The CTE + UPDATE below does
        # the same work in two SQL statements that run in seconds. Same
        # behavior: Buildings with no matching PAD entries end up with
        # pad_addresses = '' (cleared by the first UPDATE and never reset).
        logger.info('Annotating Buildings with PAD addresses (SQL aggregation)')
        with transaction.atomic(), connection.cursor() as c:
            c.execute("UPDATE datasets_building SET pad_addresses = ''")
            cleared = c.rowcount
            c.execute("""
                WITH agg AS (
                    SELECT
                        bin AS building_bin,
                        STRING_AGG(
                            COALESCE(lhnd, '') || '-' || COALESCE(hhnd, '') || ' ' || COALESCE(stname, ''),
                            ','
                        ) AS addresses
                    FROM datasets_padrecord
                    WHERE bin IS NOT NULL
                    GROUP BY bin
                )
                UPDATE datasets_building AS b
                SET pad_addresses = agg.addresses
                FROM agg
                WHERE b.bin = agg.building_bin
            """)
            updated = c.rowcount
        logger.info(
            'annotate_buildings: cleared pad_addresses on %d rows, repopulated on %d',
            cleared, updated,
        )

    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), borough='boro'))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        self.bulk_seed(**kwargs, ignore_conflict=True, overwrite=True)
        self.annotate_buildings()  # add pad addresses to building model

        # PAD chain finale: schedule the AddressRecord rebuild now that
        # Property + Building + PAD are fresh. Goes through the same
        # `core.models.Update` → `async_seed_table` celery path the admin
        # uses; the rebuild runs in its own worker so this task can finish.
        from datasets.models import AddressRecord
        AddressRecord.create_async_update_worker()

    @classmethod
    def fetch_last_updated(cls):
        return fetch_pad_last_updated(cls.download_endpoint)

    @classmethod
    def download(cls, endpoint=None, file_name=None):
        return download_pad_bobaadr_csv(
            dataset=cls.get_dataset(),
            url=endpoint or cls.download_endpoint,
        )

    @classmethod
    def create_async_update_worker(cls, endpoint=None, file_name=None):
        async_download_and_update.delay(
            cls.get_dataset().id, endpoint=endpoint, file_name=file_name)

    def __str__(self):
        return str(self.key)
