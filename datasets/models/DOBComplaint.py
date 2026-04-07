from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets import models as ds
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
from django.db.models import Subquery, OuterRef
import logging
import datetime
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
    base_download_endpoint = "https://data.cityofnewyork.us/resource/eabe-havv.csv"

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
    def download(cls, endpoint=None, file_name=None):
        two_months_ago = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%m/%d/%Y')

        query_params = (
            f"$select=complaint_number,status,date_entered,house_number,zip_code,house_street,"
            f"community_board,special_district,complaint_category,unit,disposition_date,"
            f"disposition_code,inspection_date,dobrundate,bin"
            f"&$where=(date_entered >= '{two_months_ago}' OR disposition_date >= '{two_months_ago}') AND complaint_number IS NOT NULL"
            f"&$limit=100000000"
        )

        download_url = f"{cls.base_download_endpoint}?{query_params}"
        logger.info("Downloading DOB Complaint data - past 2 months by date_entered")
        return cls.download_file(download_url, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            complaintnumber = row.get('complaintnumber')
            if is_null(complaintnumber):
                logger.warning(f"Skipping row with null complaintnumber: {row}")
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
        logger.info("Seeding/Updating %s", self.__name__)
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
