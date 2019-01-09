from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging

logger = logging.getLogger('app')


class DOBViolation(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/3h2n-5cm9/rows.csv?accessType=DOWNLOAD"

    isndobbisviol = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    boro = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    issuedate = models.DateTimeField(db_index=True, blank=True, null=True)
    violationtypecode = models.TextField(db_index=True, blank=True, null=True)
    violationnumber = models.TextField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    dispositiondate = models.DateTimeField(db_index=True, blank=True, null=True)
    dispositioncomments = models.TextField(blank=True, null=True)
    devicenumber = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ecbnumber = models.TextField(db_index=True, blank=True, null=True)
    number = models.TextField(blank=True, null=True)
    violationcategory = models.TextField(db_index=True, blank=True, null=True)
    violationtype = models.TextField(db_index=True, blank=True, null=True)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['isndobbisviol']):
                continue
            if 'bbl' in row:
                row['bbl'] = str(row['bbl'])
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if is_older_than(row[headers.index('ISSUE_DATE')], 4):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path), borough='boro'))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating {}", self.__name__)
        return self.seed_or_update_from_set_diff(**kwargs)

    def __str__(self):
        return str(self.violationid)
