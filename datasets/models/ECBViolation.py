from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging

logger = logging.getLogger('app')


class ECBViolation(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/6bgk-3dad/rows.csv?accessType=DOWNLOAD"

    ecbviolationnumber = models.TextField(primary_key=True, blank=False, null=False)
    isndobbisextract = models.ForeignKey('DOBViolation', db_column='isndobbisextract', db_constraint=False,
                                         on_delete=models.SET_NULL, null=True, blank=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    ecbviolationstatus = models.TextField(db_index=True, blank=True, null=True)
    dobviolationnumber = models.TextField(blank=True, null=True)  # not reliable FK
    boro = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    hearingdate = models.DateTimeField(db_index=True, blank=True, null=True)
    hearingtime = models.TextField(blank=True, null=True)
    serveddate = models.DateTimeField(db_index=True, blank=True, null=True)
    issuedate = models.DateTimeField(db_index=True, blank=True, null=True)
    severity = models.TextField(blank=True, null=True)
    violationtype = models.TextField(db_index=True, blank=True, null=True)
    respondentname = models.TextField(blank=True, null=True)
    respondenthousenumber = models.TextField(blank=True, null=True)
    respondentstreet = models.TextField(blank=True, null=True)
    respondentcity = models.TextField(blank=True, null=True)
    respondentzip = models.TextField(blank=True, null=True)
    violationdescription = models.TextField(blank=True, null=True)
    penalityimposed = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    amountpaid = models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True)
    balancedue = models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True)
    infractioncode1 = models.TextField(blank=True, null=True)
    sectionlawdescription1 = models.TextField(blank=True, null=True)
    infractioncode2 = models.TextField(blank=True, null=True)
    sectionlawdescription2 = models.TextField(blank=True, null=True)
    infractioncode3 = models.TextField(blank=True, null=True)
    sectionlawdescription3 = models.TextField(blank=True, null=True)
    infractioncode4 = models.TextField(blank=True, null=True)
    sectionlawdescription4 = models.TextField(blank=True, null=True)
    infractioncode5 = models.TextField(blank=True, null=True)
    sectionlawdescription5 = models.TextField(blank=True, null=True)
    infractioncode6 = models.TextField(blank=True, null=True)
    sectionlawdescription6 = models.TextField(blank=True, null=True)
    infractioncode7 = models.TextField(blank=True, null=True)
    sectionlawdescription7 = models.TextField(blank=True, null=True)
    infractioncode8 = models.TextField(blank=True, null=True)
    sectionlawdescription8 = models.TextField(blank=True, null=True)
    infractioncode9 = models.TextField(blank=True, null=True)
    sectionlawdescription9 = models.TextField(blank=True, null=True)
    infractioncode10 = models.TextField(blank=True, null=True)
    sectionlawdescription10 = models.TextField(blank=True, null=True)
    aggravatedlevel = models.TextField(blank=True, null=True)
    hearingstatus = models.TextField(blank=True, null=True)
    certificationstatus = models.TextField(blank=True, null=True)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['ecbviolationnumber']):
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
