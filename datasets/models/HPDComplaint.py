from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
from django.db.models import OuterRef, Subquery
from datasets import models as ds
from django.dispatch import receiver
from core.tasks import async_download_and_update


import logging
logger = logging.getLogger('app')


class HPDComplaint(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-receiveddate']),
            models.Index(fields=['-receiveddate']),

        ]
    API_ID = 'ygpa-z7cr'
    download_endpoint = "https://data.cityofnewyork.us/resource/ygpa-z7cr.csv"
    QUERY_DATE_KEY = 'receiveddate'
    RECENT_DATE_PINNED = True
    receiveddate = models.DateField(blank=True, null=True, verbose_name="Date when the complaint was received")
    problem_id = models.IntegerField(primary_key=True, blank=False, null=False, verbose_name="Unique identifier of this problem")
    complaint_id = models.IntegerField(blank=True, null=True, verbose_name="Unique identifier of the complaint this problem is associated with")
    building_id = models.ForeignKey('HPDBuildingRecord', db_column='buildingid', db_constraint=False, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unique identifier given to a building record")
    borough = models.TextField(choices=[('Manhattan', 'Manhattan'), ('Bronx', 'Bronx'), ('Brooklyn', 'Brooklyn'), ('Queens', 'Queens'), ('Staten Island', 'Staten Island')])
    house_number = models.TextField(verbose_name="Complaint house number")
    street_name = models.TextField(verbose_name="Complaint street name")
    zip = models.TextField(verbose_name="Complaint zip code")
    block = models.TextField(verbose_name="Number assigned by the NYC Dept of Finance identifying the tax block the lot is on")
    lot = models.TextField(verbose_name="Unique number assigned by the NYC Dept of Finance within a Block identifying a lot")
    apartment = models.TextField(verbose_name="Number of the unit or apartment in a building")
    community_board = models.IntegerField(choices=[(i, i) for i in range(1, 19)], verbose_name="Unique number identifying a Community District/Board, which is a political geographical area within a borough of the City of NY")
    unit_type = models.TextField(choices=[('Apartment', 'Apartment'), ('Building', 'Building'), ('Building-Wide', 'Building-Wide'), ('Public area', 'Public area')], verbose_name="Type of space where the problem was reported")
    space_type = models.TextField(verbose_name="Type of space where the problem was reported")
    type = models.TextField(choices=[('Emergency', 'Emergency'), ('Hazardous', 'Hazardous'), ('Immediate Emergency', 'Immediate Emergency'), ('Non emergency', 'Non emergency')], verbose_name="Code indicating the problem type")
    major_category = models.TextField(verbose_name="The major category of the problem")
    minor_category = models.TextField(verbose_name="The minor category of the problem")
    problem_code = models.TextField(verbose_name="The problem code")
    complaint_status = models.TextField(choices=[('Close', 'Close'), ('Open', 'Open')], verbose_name="The status of the complaint")
    complaint_status_date = models.DateField(blank=True, null=True, verbose_name="Date when the complaint status was updated")
    problem_status = models.TextField(choices=[('Close', 'Close'), ('Open', 'Open')], verbose_name="The status of the problem")
    problem_status_date = models.DateField(blank=True, null=True, verbose_name="Date when the problem status was updated")
    status_description = models.TextField(verbose_name="Status description")
    problem_duplicate_flag = models.TextField(choices=[('N', 'No'), ('Y', 'Yes')], verbose_name="Duplicate complaint Indicator")
    complaint_anonymous_flag = models.TextField(choices=[('N', 'No'), ('Y', 'Yes')], verbose_name="Anonymous complaint Indicator")
    unique_key = models.IntegerField(blank=True, null=True, verbose_name="Unique identifier of a Service Request (SR) in the open data set")
    
    # Foreign keys from previous datasets
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False, on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False, on_delete=models.SET_NULL, null=True, blank=True)
    
    slim_query_fields = ["complaintid", "bbl", "receiveddate"]

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
            if is_null(row['complaintid']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if headers.index('StatusDate') and is_older_than(row[headers.index('StatusDate')], 4):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), allow_blank=True))

    @classmethod
    def add_bins_from_buildingid(self):
        logger.debug(" * Adding BINs through building for HPD Complaints.")
        bin = ds.HPDBuildingRecord.objects.filter(
            buildingid=OuterRef('buildingid')).values_list('bin')[:1]
        self.objects.prefetch_related(
            'buildingid').all().update(bin=Subquery(bin))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.seed_with_upsert(callback=self.add_bins_from_buildingid, **kwargs)

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_month_offset()

    def __str__(self):
        return str(self.complaintid)


@receiver(models.signals.post_save, sender=HPDComplaint)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = sender.annotate_property_month_offset(
                instance.bbl.propertyannotation)
            annotation.save()
        except Exception as e:
            print(e)
