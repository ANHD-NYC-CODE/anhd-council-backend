from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than, does_not_contain_values
import logging

logger = logging.getLogger('app')


class DOBPermitIssuedLegacy(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/ipu4-2q9a/rows.csv?accessType=DOWNLOAD"

    job = models.TextField(blank=False, null=False)
    permitsino = models.TextField(blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    house = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    jobdoc = models.TextField(blank=True, null=True)
    jobtype = models.TextField(db_index=True, blank=True, null=True)
    selfcert = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    communityboard = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    bldgtype = models.TextField(blank=True, null=True)
    residential = models.TextField(db_index=True, blank=True, null=True)
    specialdistrict1 = models.TextField(blank=True, null=True)
    specialdistrict2 = models.TextField(blank=True, null=True)
    worktype = models.TextField(blank=True, null=True)
    permitstatus = models.TextField(db_index=True, blank=True, null=True)
    filingstatus = models.TextField(db_index=True, blank=True, null=True)
    permittype = models.TextField(blank=True, null=True)
    permitsequence = models.TextField(blank=True, null=True)
    permitsubtype = models.TextField(blank=True, null=True)
    oilgas = models.TextField(blank=True, null=True)
    sitefill = models.TextField(blank=True, null=True)
    filingdate = models.DateTimeField(db_index=True, blank=True, null=True)
    issuancedate = models.DateTimeField(db_index=True, blank=True, null=True)
    expirationdate = models.DateTimeField(blank=True, null=True)
    jobstartdate = models.DateTimeField(blank=True, null=True)
    permitteesfirstname = models.TextField(blank=True, null=True)
    permitteeslastname = models.TextField(blank=True, null=True)
    permitteesbusinessname = models.TextField(blank=True, null=True)
    permitteesphone = models.TextField(blank=True, null=True)
    permitteeslicensetype = models.TextField(blank=True, null=True)
    permitteeslicense = models.TextField(blank=True, null=True)
    actassuperintendent = models.TextField(blank=True, null=True)
    permitteesothertitle = models.TextField(blank=True, null=True)
    hiclicense = models.TextField(blank=True, null=True)
    sitesafetymgrsfirstname = models.TextField(blank=True, null=True)
    sitesafetymgrslastname = models.TextField(blank=True, null=True)
    sitesafetymgrbusinessname = models.TextField(blank=True, null=True)
    superintendentfirstlastname = models.TextField(blank=True, null=True)
    superintendentbusinessname = models.TextField(blank=True, null=True)
    ownersbusinesstype = models.TextField(blank=True, null=True)
    nonprofit = models.TextField(blank=True, null=True)
    ownersbusinessname = models.TextField(blank=True, null=True)
    ownersfirstname = models.TextField(blank=True, null=True)
    ownerslastname = models.TextField(blank=True, null=True)
    ownershouse = models.TextField(blank=True, null=True)
    ownershousestreetname = models.TextField(blank=True, null=True)
    ownershousecity = models.TextField(blank=True, null=True)
    ownershousestate = models.TextField(blank=True, null=True)
    ownershousezipcode = models.TextField(blank=True, null=True)
    ownersphone = models.TextField(blank=True, null=True)
    dobrundate = models.DateTimeField(blank=True, null=True)
    latitude = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    ntaname = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('job', 'permitsino',)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['job']) or is_null(row['permitsino']):
                continue
            if is_null(row['issuancedate']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if is_older_than(row[headers.index('Issuance Date')], 1):
                continue
            if does_not_contain_values(["a1", "a2", "dm", "nb"], row[headers.index('Job Type')]):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        return self.seed_or_update_from_set_diff(**kwargs)

    def __str__(self):
        return str(self.job)
