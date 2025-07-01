from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.database import execute
from datasets import models as ds
from django.dispatch import receiver
import logging
from core.tasks import async_create_update
from datetime import datetime

logger = logging.getLogger('app')

# Update process: Automatic
# Update strategy: Overwrite
#
# Supertable of DOBPermitIssuedLegacy and DOBPermitIssuedNow
# First, update the child tables, then create an update in admin with this DATASET, no file needed.

# TODO rename to DOBPermitIssued


class DOBIssuedPermit(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-issuedate']),
            models.Index(fields=['-issuedate']),

        ]

    QUERY_DATE_KEY = 'issuedate'

    key = models.TextField(primary_key=True, blank=False, null=False)
    jobfilingnumber = models.TextField(blank=True, null=True)
    workpermit = models.TextField(blank=True, null=True)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    houseno = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    worktype = models.TextField(db_index=True, blank=True, null=True)
    jobdescription = models.TextField(blank=True, null=True)
    issuedate = models.DateField(blank=True, null=True)
    expirationdate = models.DateField(blank=True, null=True)
    applicantname = models.TextField(blank=True, null=True)
    applicantbusinessname = models.TextField(blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    ownerbusinessname = models.TextField(blank=True, null=True)
    foreign_key = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    filing_reason = models.TextField(blank=True, null=True)
    permit_type = models.TextField(blank=True, null=True)
    permit_subtype = models.TextField(blank=True, null=True)
    permit_status = models.TextField(blank=True, null=True)
    filing_status = models.TextField(blank=True, null=True)

    slim_query_fields = ["key", "bbl", "issuedate"]

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_create_update.delay(self.get_dataset().id)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        return gen_rows

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def upsert_permit_sql(self, other_table, cols, raw_select=False):
        table_name = self._meta.db_table
        primary_key = self._meta.pk.name
        other_table_name = other_table._meta.db_table
        fields = ', '.join([k.name for k in self._meta.get_fields()])
        upsert_fields = ', '.join(
            [k.name + "=EXCLUDED." + k.name for k in self._meta.get_fields()])

        if raw_select:
            sql = "INSERT INTO {table_name} ({fields}) {cols} ON CONFLICT ({primary_key}) DO UPDATE SET {upsert_fields};"
        else:
            sql = "INSERT INTO {table_name} ({fields}) SELECT {cols} FROM {other_table_name} ON CONFLICT ({primary_key}) DO UPDATE SET {upsert_fields};"
        return sql.format(table_name=table_name, fields=fields, cols=cols, other_table_name=other_table_name, primary_key=primary_key, upsert_fields=upsert_fields)

    # Join DOBPermitIssuedLegacy table with DOBPermitIssuedNow table
    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Starting seeding/updating process for {}", self.__name__)
        
        # Add records from both tables
        legacy_table = ds.DOBPermitIssuedLegacy
        legacy_count = legacy_table.objects.count()
        logger.info("Found {} records in legacy table", legacy_count)
        
        legacy_cols = "concat({other_table_name}.job, {other_table_name}.permitsino), {other_table_name}.job, {other_table_name}.permitsino, {other_table_name}.bbl, {other_table_name}.bin, {other_table_name}.borough, {other_table_name}.house, {other_table_name}.streetname, {other_table_name}.worktype, {other_table_name}.jobtype, {other_table_name}.issuancedate, {other_table_name}.expirationdate, concat_ws(' ', {other_table_name}.permitteesfirstname, {other_table_name}.permitteeslastname), {other_table_name}.permitteesbusinessname, concat_ws(' ', {other_table_name}.ownersfirstname, {other_table_name}.ownerslastname), {other_table_name}.ownersbusinessname, {other_table_name}.id, \'{other_model_name}\', {other_table_name}.permittype, {other_table_name}.permitsubtype, {other_table_name}.permitstatus, {other_table_name}.filingstatus".format(other_table_name=legacy_table._meta.db_table, other_model_name=legacy_table._meta.model_name)

        now_table = ds.DOBPermitIssuedNow
        now_count = now_table.objects.count()
        logger.info("Found {} records in now table", now_count)
        
        now_cols = """
        SELECT DISTINCT ON (jobfilingnumber)
            concat(jobfilingnumber, workpermit) as key,
            jobfilingnumber,
            workpermit,
            bbl,
            bin,
            borough,
            houseno,
            streetname,
            worktype,
            jobdescription,
            issueddate,
            expireddate,
            concat_ws(' ', applicantfirstname, applicantlastname) as applicantname,
            applicantbusinessname,
            ownername,
            ownerbusinessname,
            id,
            'dobpermitissuednow' as type,
            filingreason as filing_reason,
            NULL as permit_type,
            NULL as permit_subtype,
            NULL as permit_status,
            NULL as filing_status
        FROM {other_table_name}
        ORDER BY jobfilingnumber, issueddate DESC
        """.format(other_table_name=now_table._meta.db_table)

        kwargs['update'].total_rows = legacy_count + now_count
        kwargs['update'].save()
        logger.info("Total records to process: {}", kwargs['update'].total_rows)

        # Process legacy records
        starting_count = self.objects.count()
        logger.info("Starting legacy table import. Current count: {}", starting_count)
        try:
            execute(self.upsert_permit_sql(legacy_table, legacy_cols))
            rows_created_legacy = self.objects.count() - starting_count
            logger.info("Legacy import complete. Created: {}, Updated: {}", 
                       rows_created_legacy, legacy_count - rows_created_legacy)
        except Exception as e:
            logger.error("Error during legacy import: {}", str(e))
            raise
        
        kwargs['update'].rows_created = kwargs['update'].rows_created + rows_created_legacy
        kwargs['update'].rows_updated = kwargs['update'].rows_updated + (legacy_count - rows_created_legacy)
        kwargs['update'].save()

        # Process now records
        starting_count = self.objects.count()
        logger.info("Starting now table import. Current count: {}", starting_count)
        try:
            execute(self.upsert_permit_sql(now_table, now_cols, raw_select=True))
            rows_created_now = self.objects.count() - starting_count
            logger.info("Now import complete. Created: {}, Updated: {}", 
                       rows_created_now, now_count - rows_created_now)
        except Exception as e:
            logger.error("Error during now import: {}", str(e))
            raise
        
        kwargs['update'].rows_created = kwargs['update'].rows_created + rows_created_now
        kwargs['update'].rows_updated = kwargs['update'].rows_updated + (now_count - rows_created_now)
        kwargs['update'].save()

        dataset = self.get_dataset()
        dataset.api_last_updated = datetime.today()
        dataset.save()
        
        final_count = self.objects.count()
        logger.info("✅ Seeding complete for {}. Final counts:", self.__name__)
        logger.info("📊 Total records: {}", final_count)
        logger.info("📊 Records created: {}", kwargs['update'].rows_created)
        logger.info("📊 Records updated: {}", kwargs['update'].rows_updated)
        logger.info("📊 Legacy records: {}", legacy_count)
        logger.info("📊 Now records: {}", now_count)

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_standard()

    def __str__(self):
        return str(self.key)


@receiver(models.signals.post_save, sender=DOBIssuedPermit)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:

            annotation = sender.annotate_property_standard(
                instance.bbl.propertyannotation)
            annotation.save()
        except Exception as e:
            print(e)
