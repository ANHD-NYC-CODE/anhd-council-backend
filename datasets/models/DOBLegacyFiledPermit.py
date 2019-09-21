from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than, does_not_contain_values
from core.tasks import async_download_and_update


import logging
logger = logging.getLogger('app')

# Update process: Automatic
# Update strategy: Overwrite
#


class DOBLegacyFiledPermit(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/ic3t-wcy2/rows.csv?accessType=DOWNLOAD"
    API_ID = 'ic3t-wcy2'

    class Meta:
        indexes = [
            #     models.Index(fields=['bbl', 'dobrundate']),  # obsolete
            #     models.Index(fields=['dobrundate', 'bbl']),  # obsolete
            #     models.Index(fields=['bbl', 'prefilingdate']),
            #     models.Index(fields=['prefilingdate', 'bbl']),
            #
        ]

    job = models.TextField(blank=False, null=False)
    jobs1no = models.TextField(blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    doc = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    house = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    jobtype = models.TextField(blank=True, null=True)
    jobstatus = models.TextField(blank=True, null=True)
    jobstatusdescrp = models.TextField(blank=True, null=True)
    latestactiondate = models.DateField(blank=True, null=True)
    buildingtype = models.TextField(blank=True, null=True)
    communityboard = models.TextField(blank=True, null=True)
    cluster = models.TextField(blank=True, null=True)
    landmarked = models.TextField(blank=True, null=True)
    adultestab = models.TextField(blank=True, null=True)
    loftboard = models.TextField(blank=True, null=True)
    cityowned = models.TextField(blank=True, null=True)
    littlee = models.TextField(blank=True, null=True)
    pcfiled = models.TextField(blank=True, null=True)
    efilingfiled = models.TextField(blank=True, null=True)
    plumbing = models.TextField(blank=True, null=True)
    mechanical = models.TextField(blank=True, null=True)
    boiler = models.TextField(blank=True, null=True)
    fuelburning = models.TextField(blank=True, null=True)
    fuelstorage = models.TextField(blank=True, null=True)
    standpipe = models.TextField(blank=True, null=True)
    sprinkler = models.TextField(blank=True, null=True)
    firealarm = models.TextField(blank=True, null=True)
    equipment = models.TextField(blank=True, null=True)
    firesuppression = models.TextField(blank=True, null=True)
    curbcut = models.TextField(blank=True, null=True)
    other = models.TextField(blank=True, null=True)
    otherdescription = models.TextField(blank=True, null=True)
    applicantsfirstname = models.TextField(blank=True, null=True)
    applicantslastname = models.TextField(blank=True, null=True)
    applicantprofessionaltitle = models.TextField(blank=True, null=True)
    applicantlicense = models.TextField(blank=True, null=True)
    professionalcert = models.TextField(blank=True, null=True)
    prefilingdate = models.DateField(blank=True, null=True)
    paid = models.TextField(blank=True, null=True)
    fullypaid = models.TextField(blank=True, null=True)
    assigned = models.TextField(blank=True, null=True)
    approved = models.TextField(blank=True, null=True)
    fullypermitted = models.TextField(blank=True, null=True)
    initialcost = models.TextField(blank=True, null=True)
    totalestfee = models.TextField(blank=True, null=True)
    feestatus = models.TextField(blank=True, null=True)
    existingzoningsqft = models.IntegerField(blank=True, null=True)
    proposedzoningsqft = models.IntegerField(blank=True, null=True)
    horizontalenlrgmt = models.IntegerField(blank=True, null=True)
    verticalenlrgmt = models.IntegerField(blank=True, null=True)
    enlargementsqfootage = models.IntegerField(blank=True, null=True)
    streetfrontage = models.IntegerField(blank=True, null=True)
    existingnoofstories = models.IntegerField(blank=True, null=True)
    proposednoofstories = models.IntegerField(blank=True, null=True)
    existingheight = models.IntegerField(blank=True, null=True)
    proposedheight = models.IntegerField(blank=True, null=True)
    existingdwellingunits = models.IntegerField(blank=True, null=True)
    proposeddwellingunits = models.IntegerField(blank=True, null=True)
    existingoccupancy = models.TextField(blank=True, null=True)
    proposedoccupancy = models.TextField(blank=True, null=True)
    sitefill = models.TextField(blank=True, null=True)
    zoningdist1 = models.TextField(blank=True, null=True)
    zoningdist2 = models.TextField(blank=True, null=True)
    zoningdist3 = models.TextField(blank=True, null=True)
    specialdistrict1 = models.TextField(blank=True, null=True)
    specialdistrict2 = models.TextField(blank=True, null=True)
    ownertype = models.TextField(blank=True, null=True)
    nonprofit = models.TextField(blank=True, null=True)
    ownersfirstname = models.TextField(blank=True, null=True)
    ownerslastname = models.TextField(blank=True, null=True)
    ownersbusinessname = models.TextField(blank=True, null=True)
    ownershousenumber = models.TextField(blank=True, null=True)
    ownershousestreetname = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    ownersphone = models.TextField(blank=True, null=True)
    jobdescription = models.TextField(blank=True, null=True)
    dobrundate = models.DateField(blank=True, null=True)
    totalconstructionfloorarea = models.TextField(blank=True, null=True)
    withdrawalflag = models.TextField(blank=True, null=True)
    signoffdate = models.DateField(blank=True, null=True)
    specialactionstatus = models.TextField(blank=True, null=True)
    specialactiondate = models.DateField(blank=True, null=True)
    buildingclass = models.TextField(blank=True, null=True)
    jobnogoodcount = models.TextField(blank=True, null=True)
    gislatitude = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    gislongitude = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    giscouncildistrict = models.TextField(blank=True, null=True)
    giscensustract = models.TextField(blank=True, null=True)
    gisntaname = models.TextField(blank=True, null=True)
    gisbin = models.TextField(blank=True, null=True)

    slim_query_fields = ["id", "bbl", "dobrundate"]

    # class Meta:
    #     unique_together = ('job', 'jobs1no',)

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['job']) or is_null(row['jobs1no']):
                continue
            if is_null(row['latestactiondate']):
                continue
            # if does_not_contain_values(["a1", "a2", "dm", "nb"], row["jobtype"]):
            #     continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            # if is_older_than(row[headers.index('Latest Action Date')], 1):
            #     continue
            # if does_not_contain_values(["a1", "a2", "dm", "nb"], row[headers.index('Job Type')]):
            #     continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.job)
