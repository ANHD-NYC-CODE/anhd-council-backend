from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
from django.db.models import OuterRef, Subquery
from datasets import models as ds
from django.dispatch import receiver
from core.tasks import async_download_and_update
from core.utils.typecast import HPDComplaintTypecast


import logging
logger = logging.getLogger('app')


class HPDComplaint(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-receiveddate']),
            models.Index(fields=['-receiveddate']),
        ]
    API_ID = 'ygpa-z7cr'
    download_endpoint = "https://data.cityofnewyork.us/api/views/ygpa-z7cr/rows.csv?accessType=DOWNLOAD"
    QUERY_DATE_KEY = 'receiveddate'
    RECENT_DATE_PINNED = True


# OLD HPD COMPLAINT MODEL DEFS:
    #  complaintid = models.IntegerField(
    #  primary_key=True, blank=False, null=False)
    #  bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
    #     on_delete=models.SET_NULL, null=True, blank=False)
    #  bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
    #    on_delete=models.SET_NULL, null=True, blank=True)
    #  buildingid = models.ForeignKey('HPDBuildingRecord', db_column='buildingid', db_constraint=False,
    #    on_delete=models.SET_NULL, null=True, blank=True)
    #  boroughid = models.IntegerField(blank=True, null=True)
    #  borough = models.TextField(blank=True, null=True)
    #  housenumber = models.TextField(blank=True, null=True)
    #  streetname = models.TextField(blank=True, null=True)
    #  zip = models.TextField(blank=True, null=True)
    #  block = models.IntegerField(blank=True, null=True)
    #  lot = models.IntegerField(blank=True, null=True)
    #  apartment = models.TextField(blank=True, null=True)
    #  communityboard = models.IntegerField(blank=True, null=True)
    #  receiveddate = models.DateField(blank=True, null=True)
    #  statusid = models.IntegerField(blank=True, null=True)
    #  status = models.TextField(db_index=True, blank=True, null=True)
    #  statusdate = models.DateField(blank=True, null=True)

# OLD HPD PROBLEM DEFS from PROBLEM model:
#     problemid = models.IntegerField(primary_key=True, blank=False, null=False)
#     complaintid = models.ForeignKey('HPDComplaint', db_column='complaintid', db_constraint=False,on_delete=models.SET_NULL, null=True, blank=False)
#     unittypeid = models.SmallIntegerField(blank=True, null=True)
#     unittype = models.TextField(blank=True, null=True)
#     spacetypeid = models.SmallIntegerField(blank=True, null=True)
#     spacetype = models.TextField(blank=True, null=True)
#     typeid = models.SmallIntegerField(blank=True, null=True)
#     type = models.TextField(blank=True, null=True)
#     majorcategoryid = models.SmallIntegerField(blank=True, null=True)
#     majorcategory = models.TextField(blank=True, null=True)
#     minorcategoryid = models.SmallIntegerField(blank=True, null=True)
#     minorcategory = models.TextField(blank=True, null=True)
#     codeid = models.SmallIntegerField(blank=True, null=True)
#     code = models.TextField(blank=True, null=True)
#     statusid = models.IntegerField(db_index=True, blank=True, null=True)
#     status = models.TextField(db_index=True, blank=True, null=True)
#     statusdate = models.DateField(db_index=True, blank=True, null=True)
#     statusdescription = models.TextField(blank=True, null=True)

    # Updated Model Fields
    zip = models.TextField(null=True, verbose_name="Complaint zip code")
    receiveddate = models.DateField(
        blank=True, null=True, verbose_name="Date when the complaint was received")
    problemid = models.IntegerField(
        primary_key=True, blank=False, null=False, verbose_name="Unique identifier of this problem")
    # This was previously a primary key in the HPDComplaint table, and because HPD Complaint IDs are now longer unique, we will use the Problem ID as the primary key for this table.
    complaintid = models.IntegerField(
        blank=True, null=True, verbose_name="identifier of the complaint this problem is associated with")
    council_district = models.IntegerField(
        null=True, blank=True, verbose_name="Council district of the complaint location")
    census_tract = models.IntegerField(
        null=True, blank=True, verbose_name="Census tract of the complaint location")
    nta = models.TextField(
        null=True, blank=True, verbose_name="Neighborhood Tabulation Area of the complaint location")
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            default=0, on_delete=models.SET_NULL, null=True, blank=True)
    buildingid = models.ForeignKey('HPDBuildingRecord', db_column='buildingid', db_constraint=False,
                                   on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unique identifier given to a building record")
    borough = models.TextField(choices=[('Manhattan', 'Manhattan'), ('Bronx', 'Bronx'), (
        'Brooklyn', 'Brooklyn'), ('Queens', 'Queens'), ('Staten Island', 'Staten Island')])
    housenumber = models.TextField(
        null=True, verbose_name="Complaint house number")
    streetname = models.TextField(
        null=True, verbose_name="Complaint street name")
    latitude = models.DecimalField(max_digits=20, decimal_places=15, null=True,
                                   blank=True, verbose_name="Latitude of the complaint location")
    longitude = models.DecimalField(max_digits=20, decimal_places=15, null=True,
                                    blank=True, verbose_name="Longitude of the complaint location")
    block = models.TextField(
        null=True, verbose_name="Number assigned by the NYC Dept of Finance identifying the tax block the lot is on")
    lot = models.TextField(
        null=True, verbose_name="Unique number assigned by the NYC Dept of Finance within a Block identifying a lot")
    apartment = models.TextField(
        null=True, verbose_name="Number of the unit or apartment in a building")
    communityboard = models.IntegerField(choices=[(i, i) for i in range(
        1, 19)], null=True, verbose_name="Unique number identifying a  Community District/Board, which is a political geographical area within a borough of the City of NY")
    unittype = models.TextField(choices=[('Apartment', 'Apartment'), ('Building', 'Building'), ('Building-Wide', 'Building-Wide'),
                                ('Public area', 'Public area')], null=True, verbose_name="Type of space where the problem was reported")
    spacetype = models.TextField(
        null=True, verbose_name="Type of space where the problem was reported")
    type = models.TextField(choices=[('Emergency', 'Emergency'), ('Hazardous', 'Hazardous'), ('Immediate Emergency',
                            'Immediate Emergency'), ('Non emergency', 'Non emergency')], null=True, verbose_name="Code indicating the problem type")
    majorcategory = models.TextField(
        null=True, verbose_name="The major category of the problem")
    minorcategory = models.TextField(
        null=True, verbose_name="The minor category of the problem")
    code = models.TextField(null=True, verbose_name="The problem code")
    status = models.TextField(choices=[(
        'Close', 'Close'), ('Open', 'Open')], null=True, verbose_name="The status of the complaint")
    statusdate = models.DateField(
        blank=True, null=True, verbose_name="Date when the complaint status was updated")
    problemstatus = models.TextField(choices=[(
        'Close', 'Close'), ('Open', 'Open')], null=True, verbose_name="The status of the problem")
    problemstatusdate = models.DateField(
        blank=True, null=True, verbose_name="Date when the problem status was updated")
    statusdescription = models.TextField(
        null=True, verbose_name="Status description")
    problemduplicateflag = models.TextField(choices=[(
        'N', 'No'), ('Y', 'Yes')], null=True, verbose_name="Duplicate complaint Indicator")
    complaintanonymousflag = models.TextField(choices=[(
        'N', 'No'), ('Y', 'Yes')], null=True, verbose_name="Anonymous complaint Indicator")
    uniquekey = models.IntegerField(
        blank=True, null=True, verbose_name="Unique identifier of a Service Request (SR) in the open data set")

    # complaint status is still mapped to this table's "status", but the prior "status" from the HPDProblem table has become "problem_status" and "problem_status_date" and will need to be mapped to the those fields across the app instead of HPD Problems.

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
        typecaster = HPDComplaintTypecast(HPDComplaint)
        for row in gen_rows:
            if not is_null(row['complaintid']):
                yield typecaster.cast_row(row)

    # trims down new update files to preserve memory
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        typecaster = HPDComplaintTypecast(HPDComplaint)
        for row in csv_reader:
            # Check and handle complaint status date
            complaint_status_date_key = 'complaint_status_date' if 'complaint_status_date' in headers else 'statusdate'
            if complaint_status_date_key in headers:
                status_date_index = headers.index(complaint_status_date_key)
                if is_older_than(row[status_date_index], 4):
                    continue
            yield typecaster.cast_row(row)

    # remapping new csv column names to old column names to preserve app structure
    COLUMN_NAME_MAPPING = {
        "complaintid": "complaint_id",
        "buildingid": "building_id",
        "borough": "borough",
        "housenumber": "house_number",
        "streetname": "street_name",
        "communityboard": "community_board",
        "receiveddate": "received_date",
        "status": "complaint_status",
        "statusdate": "complaint_status_date",
        "problemid": "problem_id",
        "unittype": "unit_type",
        "spacetype": "space_type",
        "type": "type",
        "majorcategory": "major_category",
        "minorcategory": "minor_category",
        "code": "problem_code",
        "statusdescription": "status_description",  # previously in HPDProblem
        "zip": "post_code",
    }

    # This function needs to be verified to see that it still works
    @classmethod
    def update_set_filter(cls, csv_reader, headers):
        typecaster = HPDComplaintTypecast(HPDComplaint)
        for row in csv_reader:
            # Check and handle problem status date
            if 'problemstatusdate' in headers:
                problem_status_date_index = headers.index('problemstatusdate')
                if is_older_than(row[problem_status_date_index], 1):
                    continue
            yield typecaster.cast_row(row)

    @classmethod
    def transform_self(self, file_path, update=None):
        rows = self.pre_validation_filters(
            with_bbl(from_csv_file_to_gen(file_path, update), allow_blank=True))
        typecaster = HPDComplaintTypecast(HPDComplaint)
        for row in rows:
            for new_col, old_col in HPDComplaint.COLUMN_NAME_MAPPING.items():
                if new_col in row:
                    if old_col:
                        row[old_col] = row.pop(new_col)
                    else:
                        row.pop(new_col, None)
            yield typecaster.cast_row(row)

    @classmethod
    def add_bins_from_buildingid(self):
        logger.info("Starting adding bins from building id.")
        logger.debug(" * Adding BINs through building for HPD Complaints.")
        bin = ds.HPDBuildingRecord.objects.filter(
            buildingid=OuterRef('buildingid')).values_list('bin')[:1]
        self.objects.prefetch_related(
            'buildingid').all().update(bin=Subquery(bin))
        logger.info("Completed adding bins.")

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Starting seed_with_upsert.")
        self.seed_with_upsert(callback=self.add_bins_from_buildingid, **kwargs)
        logger.info("Completed seed_with_upsert.")

    @classmethod
    def annotate_properties(self):
        logger.info("Starting annotation.")
        self.annotate_all_properties_month_offset()
        logger.info("Completed annotation.")

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
