from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets import models as ds
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
from django.db.models import Subquery, OuterRef
import logging
from django.dispatch import receiver
from datasets import models as ds
from core.tasks import async_download_and_update

logger = logging.getLogger('app')


class DOBComplaint(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-dateentered']),
            models.Index(fields=['-dateentered']),
        ]
    API_ID = 'eabe-havv'
    QUERY_DATE_KEY = 'dateentered'

    download_endpoint = "https://nycopendata.socrata.com/api/views/eabe-havv/rows.csv?accessType=DOWNLOAD"

    complaintnumber = models.IntegerField(
        primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    status = models.TextField(db_index=True, blank=True, null=True)
    dateentered = models.DateField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    housestreet = models.TextField(blank=True, null=True)
    communityboard = models.IntegerField(blank=True, null=True)
    specialdistrict = models.TextField(blank=True, null=True)
    complaintcategory = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    dispositiondate = models.DateField(blank=True, null=True)
    dispositioncode = models.TextField(db_index=True, blank=True, null=True)
    inspectiondate = models.DateField(blank=True, null=True)
    dobrundate = models.DateField(blank=True, null=True)

    slim_query_fields = ["complaintnumber", "bbl", "dateentered"]

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['complaintnumber']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if headers.index('Date Entered') and is_older_than(row[headers.index('Date Entered')], 4):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def add_bbls_from_bin(self):
        logger.debug(" * Adding BBLs through building for DOB Complaints.")

        bbl = ds.Building.objects.filter(
            bin=OuterRef('bin')
        ).values_list(
            'bbl'
        )[:1]

        self.objects.prefetch_related(
            'building').all().update(bbl=Subquery(bbl))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        self.seed_with_upsert(callback=self.add_bbls_from_bin, **kwargs)

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_standard()

    def __str__(self):
        return str(self.complaintnumber)


@receiver(models.signals.post_save, sender=DOBComplaint)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:

            annotation = sender.annotate_property_standard(
                instance.bbl.propertyannotation)
            annotation.save()
        except Exception as e:
            print(e)
