from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging
from django.dispatch import receiver
from datasets import models as ds
from core.tasks import async_download_and_update

logger = logging.getLogger('app')


class DOBViolation(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-issuedate']),
            models.Index(fields=['-issuedate']),
        ]
    API_ID = '3h2n-5cm9'
    download_endpoint = "https://data.cityofnewyork.us/api/views/3h2n-5cm9/rows.csv?accessType=DOWNLOAD"
    QUERY_DATE_KEY = 'issuedate'
    EARLIEST_RECORD = '1901-01-01'

    isndobbisviol = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    boro = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    issuedate = models.DateField(blank=True, null=True)
    violationtypecode = models.TextField(db_index=True, blank=True, null=True)
    violationnumber = models.TextField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    dispositiondate = models.DateField(blank=True, null=True)
    dispositioncomments = models.TextField(blank=True, null=True)
    devicenumber = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ecbnumber = models.TextField(db_index=True, blank=True, null=True)
    number = models.TextField(blank=True, null=True)
    violationcategory = models.TextField(db_index=True, blank=True, null=True)
    violationtype = models.TextField(db_index=True, blank=True, null=True)

    slim_query_fields = ["isndobbisviol", "bbl", "issuedate"]

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
            if is_null(row['isndobbisviol']):
                continue

            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if row[headers.index('ISSUE_DATE')] and is_older_than(row[headers.index('ISSUE_DATE')], 4):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), borough='boro'))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        self.seed_with_upsert(**kwargs)

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_standard()

    def __str__(self):
        return str(self.isndobbisviol)


@receiver(models.signals.post_save, sender=DOBViolation)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:

            annotation = sender.annotate_property_standard(
                instance.bbl.propertyannotation)
            annotation.save()
        except Exception as e:
            print(e)
