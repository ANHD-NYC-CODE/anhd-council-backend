from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than, does_not_contain_values
import logging
from core.tasks import async_download_and_update


logger = logging.getLogger('app')

# Update process: Automatic
# Update strategy: Overwrite
#


class DOBNowFiledPermit(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/w9ak-ipjd/rows.csv?accessType=DOWNLOAD"
    API_ID = 'w9ak-ipjd'

    class Meta:
        indexes = [
            # models.Index(fields=['bbl', 'dobrundate']),
            # models.Index(fields=['dobrundate', 'bbl']),
            # models.Index(fields=['bbl', 'prefilingdate']),
            # models.Index(fields=['prefilingdate', 'bbl']),
        ]

    jobfilingnumber = models.TextField(blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    filingstatus = models.TextField(blank=True, null=True)
    houseno = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    commmunityboard = models.TextField(blank=True, null=True)
    workonfloor = models.TextField(blank=True, null=True)
    aptcondonos = models.TextField(blank=True, null=True)
    applicantprofessionaltitle = models.TextField(blank=True, null=True)
    applicantlicense = models.TextField(blank=True, null=True)
    applicantfirstname = models.TextField(blank=True, null=True)
    applicantsmiddleinitial = models.TextField(blank=True, null=True)
    applicantlastname = models.TextField(blank=True, null=True)
    ownersbusinessname = models.TextField(blank=True, null=True)
    ownersstreetname = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    filingrepresentativefirstname = models.TextField(blank=True, null=True)
    filingrepresentativemiddleinitial = models.TextField(blank=True, null=True)
    filingrepresentativelastname = models.TextField(blank=True, null=True)
    filingrepresentativebusinessname = models.TextField(blank=True, null=True)
    filingrepresentativestreetname = models.TextField(blank=True, null=True)
    filingrepresentativecity = models.TextField(blank=True, null=True)
    filingrepresentativestate = models.TextField(blank=True, null=True)
    filingrepresentativezip = models.TextField(blank=True, null=True)
    sprinklerworktype = models.BooleanField(blank=True, null=True)
    plumbingworktype = models.BooleanField(blank=True, null=True)
    initialcost = models.IntegerField(blank=True, null=True)
    totalconstructionfloorarea = models.IntegerField(blank=True, null=True)
    reviewbuildingcode = models.IntegerField(blank=True, null=True)
    littlee = models.BooleanField(blank=True, null=True)
    unmappedccostreet = models.BooleanField(blank=True, null=True)
    requestlegalization = models.BooleanField(blank=True, null=True)
    includespermanentremoval = models.BooleanField(blank=True, null=True)
    incompliancewithnycecc = models.BooleanField(blank=True, null=True)
    exemptfromnycecc = models.BooleanField(blank=True, null=True)
    buildingtype = models.TextField(blank=True, null=True)
    existingstories = models.IntegerField(blank=True, null=True)
    existingheight = models.IntegerField(blank=True, null=True)
    existingdwellingunits = models.IntegerField(blank=True, null=True)
    proposednoofstories = models.IntegerField(blank=True, null=True)
    proposedheight = models.IntegerField(blank=True, null=True)
    proposeddwellingunits = models.IntegerField(blank=True, null=True)
    specialinspectionrequirement = models.TextField(blank=True, null=True)
    specialinspectionagencynumber = models.TextField(blank=True, null=True)
    progressinspectionrequirement = models.TextField(blank=True, null=True)
    built1informationvalue = models.TextField(blank=True, null=True)
    built2informationvalue = models.TextField(blank=True, null=True)
    built2ainformationvalue = models.TextField(blank=True, null=True)
    built2binformationvalue = models.TextField(blank=True, null=True)
    standpipe = models.BooleanField(blank=True, null=True)
    antenna = models.BooleanField(blank=True, null=True)
    curbcut = models.BooleanField(blank=True, null=True)
    sign = models.BooleanField(blank=True, null=True)
    fence = models.BooleanField(blank=True, null=True)
    scaffold = models.BooleanField(blank=True, null=True)
    shed = models.BooleanField(blank=True, null=True)
    latitude = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    nta = models.TextField(blank=True, null=True)

    @classmethod
    def create_async_update_worker(self):
        async_download_and_update.delay(self.get_dataset().id)

    # BIN
    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return with_bbl(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.jobfilingnumber)
