from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen
from datasets.utils.validation_filters import is_null, is_older_than
from django.dispatch import receiver
from core.tasks import async_download_and_update
from datasets import models as ds
import logging
import datetime
logger = logging.getLogger('app')


class HPDViolation(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-approveddate']),
            models.Index(fields=['-approveddate']),
        ]

    API_ID = 'wvxf-dwi5'
    base_download_endpoint = "https://data.cityofnewyork.us/resource/wvxf-dwi5.csv"
    QUERY_DATE_KEY = 'approveddate'
    EARLIEST_RECORD = '1933-01-01'

    # download_endpoint = "https://data.cityofnewyork.us/api/views/wvxf-dwi5/rows.csv?accessType=DOWNLOAD"

    violationid = models.IntegerField(
        primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    buildingid = models.ForeignKey('HPDBuildingRecord', db_column='buildingid', db_constraint=False,
                                   on_delete=models.SET_NULL, null=True, blank=True)
    registrationid = models.IntegerField(blank=True, null=True)
    boroid = models.TextField(blank=True, null=True)
    borough = models.TextField(db_index=True)
    housenumber = models.TextField()
    lowhousenumber = models.TextField(blank=True, null=True)
    highhousenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    streetcode = models.TextField(blank=True, null=True)
    postcode = models.TextField(blank=True, null=True)
    apartment = models.TextField(blank=True, null=True)
    story = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    class_name = models.TextField(blank=True, null=True)
    inspectiondate = models.DateField(blank=True, null=True)
    approveddate = models.DateField(blank=True, null=True)
    originalcertifybydate = models.DateField(blank=True, null=True)
    originalcorrectbydate = models.DateField(blank=True, null=True)
    newcertifybydate = models.DateField(blank=True, null=True)
    newcorrectbydate = models.DateField(blank=True, null=True)
    certifieddate = models.DateField(blank=True, null=True)
    ordernumber = models.TextField(blank=True, null=True)
    novid = models.IntegerField(blank=True, null=True)
    novdescription = models.TextField(blank=True, null=True)
    novissueddate = models.DateField(blank=True, null=True)
    currentstatusid = models.IntegerField(blank=True, null=True)
    currentstatus = models.TextField(db_index=True, blank=True, null=True)
    currentstatusdate = models.DateField(db_index=True, blank=True, null=True)
    novtype = models.TextField(blank=True, null=True)
    violationstatus = models.TextField(db_index=True, blank=True, null=True)
    latitude = models.DecimalField(
        decimal_places=8, max_digits=32, blank=True, null=True)
    longitude = models.DecimalField(
        decimal_places=8, max_digits=32, blank=True, null=True)
    communityboard = models.TextField(blank=True, null=True)
    councildistrict = models.IntegerField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    nta = models.TextField(blank=True, null=True)
    rentimpairing = models.TextField(default='', blank=True, null=True)

    slim_query_fields = ["violationid", "bbl", "approveddate"]

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    # Download Method for Full File (unfiltered by date)
    # @classmethod
    # def download(self, endpoint=None, file_name=None):
    #     return self.download_file(self.download_endpoint, file_name=file_name)

    # New Download method via API Soda Filtering by Date
    @classmethod
    def download(cls, endpoint=None, file_name=None):
        # Filter the CSV being downloaded from Socrata to just past year
        one_year_ago = (datetime.datetime.now(
        ) - datetime.timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S')

        # Construct the dynamic URL with query parameters
        query_params = (
            f"$where=inspectiondate >= '{one_year_ago}'"
            f"&$limit=100000000"
        )

        # Set the download_endpoint dynamically
        download_endpoint = f"{cls.base_download_endpoint}?{query_params}"

        logger.info(
            f"Downloading HPD Violation data - filtered by inspection dates in the past year -  from {download_endpoint}")

        # Use the download_file method with the dynamic URL
        return cls.download_file(download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['violationid']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if headers.index('InspectionDate') and is_older_than(row[headers.index('InspectionDate')], 1):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating {}", self.__name__)
        self.seed_with_upsert(**kwargs)

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_standard()

    def __str__(self):
        return str(self.violationid)


@receiver(models.signals.post_save, sender=HPDViolation)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = sender.annotate_property_standard(
                instance.bbl.propertyannotation)
            annotation.save()
        except Exception as e:
            print(e)
