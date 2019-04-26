from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than, does_not_contain_values
import logging
from core.tasks import async_download_and_update


logger = logging.getLogger('app')

# TODO - generate unique key during transform and add as a model field
# remove unqiue constraints beacuse it's slowing down updates a lot

# Update process: Automatic
# Update strategy: Overwrite
#


class DOBPermitIssuedNow(BaseDatasetModel, models.Model):
    API_ID = 'rbx6-tga4'
    download_endpoint = "https://data.cityofnewyork.us/api/views/rbx6-tga4/rows.csv?accessType=DOWNLOAD"

    jobfilingnumber = models.TextField(blank=True, null=True)
    workpermit = models.TextField(blank=True, null=True)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    filingreason = models.TextField(blank=True, null=True)
    houseno = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    cbno = models.TextField(blank=True, null=True)
    aptcondonos = models.TextField(blank=True, null=True)
    workonfloor = models.TextField(blank=True, null=True)
    worktype = models.TextField(blank=True, null=True)
    permitteeslicensetype = models.TextField(blank=True, null=True)
    applicantlicense = models.TextField(blank=True, null=True)
    applicantfirstname = models.TextField(blank=True, null=True)
    applicantmiddlename = models.TextField(blank=True, null=True)
    applicantlastname = models.TextField(blank=True, null=True)
    applicantbusinessname = models.TextField(blank=True, null=True)
    applicantbusinessaddress = models.TextField(blank=True, null=True)
    filingrepresentativefirstname = models.TextField(blank=True, null=True)
    filingrepresentativemiddleinitial = models.TextField(blank=True, null=True)
    filingrepresentativelastname = models.TextField(blank=True, null=True)
    filingrepresentativebusinessname = models.TextField(blank=True, null=True)
    approveddate = models.DateTimeField(blank=True, null=True)
    issueddate = models.DateTimeField(blank=True, null=True)
    expireddate = models.DateTimeField(blank=True, null=True)
    jobdescription = models.TextField(blank=True, null=True)
    estimatedjobcosts = models.TextField(blank=True, null=True)
    ownerbusinessname = models.TextField(blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    ownerstreetaddress = models.TextField(blank=True, null=True)
    ownercity = models.TextField(blank=True, null=True)
    ownerstate = models.TextField(blank=True, null=True)
    ownerzipcode = models.TextField(blank=True, null=True)

    # class Meta:
    #     unique_together = ('jobfilingnumber', 'workpermit', 'issueddate')

    @classmethod
    def create_async_update_worker(self):
        async_download_and_update.delay(self.get_dataset().id)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['jobfilingnumber']) or is_null(row['workpermit']) or is_null(row['issueddate']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if headers.index('Issued Date') and is_older_than(row[headers.index('Issued Date')], 1):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        return self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.jobfilingnumber)
