from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging

logger = logging.getLogger('app')


class Eviction(BaseDatasetModel, models.Model):
    download_endpoint = "https://s3.amazonaws.com/justfix-data/marshal_evictions_2017.csv"

    courtindex = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    boro = models.TextField(blank=True, null=True)
    docketnumber = models.TextField(blank=True, null=True)
    evictionaddress = models.TextField(blank=True, null=True)
    apt = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    uniqueid = models.TextField(blank=True, null=True)
    executeddate = models.DateTimeField(db_index=True, blank=True, null=True)
    marshalfirstname = models.TextField(blank=True, null=True)
    marshallastname = models.TextField(blank=True, null=True)
    evictiontype = models.TextField(db_index=True, blank=True, null=True)
    scheduledstatus = models.TextField(db_index=True, blank=True, null=True)
    cleanedaddress1 = models.TextField(blank=True, null=True)
    cleanedaddress2 = models.TextField(blank=True, null=True)
    lat = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    lng = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    geocoder = models.TextField(blank=True, null=True)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['courtindex']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    # Because the CSV has commas in marshalllastname column - Smith,jr.
    @classmethod
    def clean_evictions_csv(self, gen_rows):
        for row in gen_rows:
            row = row.lower().replace(',jr.', '')
            row = row.lower().replace(', jr.', '')
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update, self.clean_evictions_csv))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating {}", self.__name__)
        return self.seed_or_update_from_set_diff(**kwargs)

    def __str__(self):
        return str(self.violationid)
