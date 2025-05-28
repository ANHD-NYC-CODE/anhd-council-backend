from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, does_not_contain_values
from core.utils.database import execute
from django.dispatch import receiver
from datasets import models as ds
from core.tasks import async_create_update
from datetime import datetime
import logging

logger = logging.getLogger('app')

# Update process: Automatic
# Update strategy: Overwrite
#
# Supertable of DOBLegacyFiledPermit and DOBNowFiledPermit
# First, update the child tables, then create an update in admin with this DATASET, no file needed.


class DOBFiledPermit(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-datefiled']),
            models.Index(fields=['-datefiled']),

        ]

    QUERY_DATE_KEY = 'datefiled'

    key = models.TextField(primary_key=True, blank=False, null=False)
    jobfilingnumber = models.TextField(blank=True, null=True)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    housenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    jobstatus = models.TextField(blank=True, null=True)
    # AKA Work Type # no NOW equivalent
    jobtype = models.TextField(blank=True, null=True)  # Mapped standardized value
    job_type = models.TextField(blank=True, null=True)  # Original raw value from API
    jobdescription = models.TextField(
        blank=True, null=True)  # no NOW equivalent
    datefiled = models.DateField(
        db_index=True, blank=True, null=True)  # no NOW equivalent
    applicantsfirstname = models.TextField(blank=True, null=True)
    applicantslastname = models.TextField(blank=True, null=True)
    applicantprofessionaltitle = models.TextField(blank=True, null=True)
    applicantlicense = models.TextField(blank=True, null=True)
    ownerbusinessname = models.TextField(blank=True, null=True)
    initialcost = models.TextField(blank=True, null=True)
    foreign_key = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)

    slim_query_fields = ["id", "bbl", "datefiled"]

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_create_update.delay(self.get_dataset().id)

    @classmethod
    def upsert_permit_sql(self, other_table, cols, raw_select=False):
        table_name = self._meta.db_table
        primary_key = self._meta.pk.name
        fields = ', '.join([k.name for k in self._meta.get_fields()])
        upsert_fields = ', '.join(
            [k.name + "=EXCLUDED." + k.name for k in self._meta.get_fields()]
        )
    
        if raw_select:
            # If `cols` is a full SELECT statement already
            sql = "INSERT INTO {table_name} ({fields}) {cols} ON CONFLICT ({primary_key}) DO UPDATE SET {upsert_fields};"
        else:
            # Regular cols string (non-SELECT)
            other_table_name = other_table._meta.db_table
            sql = "INSERT INTO {table_name} ({fields}) SELECT {cols} FROM {other_table_name} ON CONFLICT ({primary_key}) DO UPDATE SET {upsert_fields};"
        
        return sql.format(
            table_name=table_name,
            fields=fields,
            cols=cols,
            other_table_name=other_table._meta.db_table if not raw_select else "",
            primary_key=primary_key,
            upsert_fields=upsert_fields
        )

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating {}", self.__name__)
        # Add records from both tables
        legacy_table = ds.DOBLegacyFiledPermit
        legacy_count = legacy_table.objects.count()
        legacy_cols = """
        concat('{other_model_name}', {other_table_name}.jobs1no, {other_table_name}.job),
        {other_table_name}.job,
        {other_table_name}.bbl,
        {other_table_name}.bin,
        {other_table_name}.house,
        {other_table_name}.streetname,
        {other_table_name}.borough,
        {other_table_name}.jobstatusdescrp,
        CASE 
            WHEN {other_table_name}.jobtype IN ('A1', 'ALT-CO', 'ALT-CO (A1)', 'Alteration CO', 'Alteration CO (A1)', 'Alteration') THEN 'ALT-CO (A1)'
            WHEN {other_table_name}.jobtype IN ('A2', 'Alteration', 'Alteration (A2)', 'Alteration A2') THEN 'Alteration (A2)'
            WHEN {other_table_name}.jobtype IN ('DM', 'Full Demolition', 'Full Demolition (DM)', 'Demolition') THEN 'Full Demolition (DM)'
            WHEN {other_table_name}.jobtype IN ('NB', 'New Building', 'New Building (NB)', 'New Building NB') THEN 'New Building (NB)'
            WHEN {other_table_name}.jobtype IN ('PA', 'No Work', 'No Work (PA)', 'No Work PA') THEN 'No Work (PA)'
            WHEN {other_table_name}.jobtype IN ('ALT-CO - New Building with Existing Elements to Remain', 'ALT-CO: New Building with Existing Elements to Remain', 'ALT-CO New Building with Existing Elements to Remain') THEN 'ALT-CO: New Building with Existing Elements to Remain'
            WHEN {other_table_name}.jobtype IN ('A3', 'SC', 'SG', 'SI') THEN {other_table_name}.jobtype
            ELSE {other_table_name}.jobtype
        END,
        {other_table_name}.jobtype,
        {other_table_name}.jobdescription,
        {other_table_name}.prefilingdate,
        {other_table_name}.applicantsfirstname,
        {other_table_name}.applicantslastname,
        {other_table_name}.applicantprofessionaltitle,
        {other_table_name}.applicantlicense,
        {other_table_name}.ownersbusinessname,
        {other_table_name}.initialcost,
        CAST({other_table_name}.id AS text),
        '{other_model_name}'
        """.format(
            other_table_name=legacy_table._meta.db_table,
            other_model_name=legacy_table._meta.model_name
        )
        now_table = ds.DOBNowFiledPermit
        now_count = now_table.objects.count()
        now_cols = """
        SELECT DISTINCT ON ({other_table_name}.jobfilingnumber)
            concat('{other_model_name}', {other_table_name}.jobfilingnumber),
            {other_table_name}.jobfilingnumber,
            {other_table_name}.bbl,
            {other_table_name}.bin,
            {other_table_name}.houseno,
            {other_table_name}.streetname,
            {other_table_name}.borough,
            {other_table_name}.filingstatus,
            CASE 
                WHEN {other_table_name}.jobtype IN ('A1', 'ALT-CO', 'ALT-CO (A1)', 'Alteration CO', 'Alteration CO (A1)', 'Alteration') THEN 'ALT-CO (A1)'
                WHEN {other_table_name}.jobtype IN ('A2', 'Alteration', 'Alteration (A2)', 'Alteration A2') THEN 'Alteration (A2)'
                WHEN {other_table_name}.jobtype IN ('DM', 'Full Demolition', 'Full Demolition (DM)', 'Demolition') THEN 'Full Demolition (DM)'
                WHEN {other_table_name}.jobtype IN ('NB', 'New Building', 'New Building (NB)', 'New Building NB') THEN 'New Building (NB)'
                WHEN {other_table_name}.jobtype IN ('PA', 'No Work', 'No Work (PA)', 'No Work PA') THEN 'No Work (PA)'
                WHEN {other_table_name}.jobtype IN ('ALT-CO - New Building with Existing Elements to Remain', 'ALT-CO: New Building with Existing Elements to Remain', 'ALT-CO New Building with Existing Elements to Remain') THEN 'ALT-CO: New Building with Existing Elements to Remain'
                WHEN {other_table_name}.jobtype IN ('A3', 'SC', 'SG', 'SI') THEN {other_table_name}.jobtype
                ELSE {other_table_name}.jobtype
            END,
            {other_table_name}.jobtype,
            {other_table_name}.workonfloor,
            {other_table_name}.filingdate,
            {other_table_name}.applicantfirstname,
            {other_table_name}.applicantlastname,
            {other_table_name}.applicantprofessionaltitle,
            {other_table_name}.applicantlicense,
            {other_table_name}.ownersbusinessname,
            {other_table_name}.initialcost,
            CAST({other_table_name}.id AS text),
            '{other_model_name}'
        FROM {other_table_name}
        ORDER BY {other_table_name}.jobfilingnumber, {other_table_name}.filingdate DESC
        """.format(
            other_table_name=now_table._meta.db_table,
            other_model_name=now_table._meta.model_name
        )

        # Clean up existing records - only updating the jobtype column
        cleanup_sql = """
        -- Only updating the jobtype column, leaving all other columns unchanged
        UPDATE {table_name}
        SET jobtype = CASE 
            WHEN jobtype IN ('A1', 'ALT-CO', 'ALT-CO (A1)', 'Alteration CO', 'Alteration CO (A1)', 'Alteration') THEN 'ALT-CO (A1)'
            WHEN jobtype IN ('A2', 'Alteration', 'Alteration (A2)', 'Alteration A2') THEN 'Alteration (A2)'
            WHEN jobtype IN ('DM', 'Full Demolition', 'Full Demolition (DM)', 'Demolition') THEN 'Full Demolition (DM)'
            WHEN jobtype IN ('NB', 'New Building', 'New Building (NB)', 'New Building NB') THEN 'New Building (NB)'
            WHEN jobtype IN ('PA', 'No Work', 'No Work (PA)', 'No Work PA') THEN 'No Work (PA)'
            WHEN jobtype IN ('ALT-CO - New Building with Existing Elements to Remain', 'ALT-CO: New Building with Existing Elements to Remain', 'ALT-CO New Building with Existing Elements to Remain') THEN 'ALT-CO: New Building with Existing Elements to Remain'
            WHEN jobtype IN ('A3', 'SC', 'SG', 'SI') THEN jobtype
            ELSE jobtype
        END
        WHERE jobtype IS NOT NULL
        AND jobtype NOT IN (
            'ALT-CO (A1)',
            'Alteration (A2)',
            'Full Demolition (DM)',
            'New Building (NB)',
            'No Work (PA)',
            'ALT-CO: New Building with Existing Elements to Remain',
            'A3',
            'SC',
            'SG',
            'SI'
        );
        """.format(table_name=self._meta.db_table)
        
        execute(cleanup_sql)
        logger.info("Cleaned up existing job types in the database")

        kwargs['update'].total_rows = legacy_count + now_count
        kwargs['update'].save()
        starting_count = self.objects.count()

        execute(self.upsert_permit_sql(legacy_table, legacy_cols))
        logger.debug("legacy seeded - current count: {}", self.objects.count())
        rows_created_legacy = self.objects.count() - starting_count
        kwargs['update'].rows_created = kwargs['update'].rows_created + \
            rows_created_legacy
        kwargs['update'].rows_updated = kwargs['update'].rows_updated + \
            (legacy_count - rows_created_legacy)
        kwargs['update'].save()
        logger.debug("Completed seed into {} for {}",
                     self.__name__, legacy_table._meta.db_table)

        starting_count = self.objects.count()
        # execute(self.upsert_permit_sql(now_table, now_cols))
        execute(self.upsert_permit_sql(now_table, now_cols, raw_select=True))
        logger.debug("now seeded - current count: {}", self.objects.count())

        rows_created_now = self.objects.count() - starting_count
        kwargs['update'].rows_created = kwargs['update'].rows_created + \
            rows_created_now
        kwargs['update'].rows_updated = kwargs['update'].rows_updated + \
            (now_count - rows_created_now)
        kwargs['update'].save()

        logger.debug("Completed seed into {} for {}",
                     self.__name__, now_table._meta.db_table)

        dataset = self.get_dataset()
        dataset.api_last_updated = datetime.today()
        dataset.save()
        total_count = self.objects.count()
        logger.info("✅ Completed seeding DOBFiledPermit. Total rows in table: %s", total_count)
        logger.info("📊 Rows created: %s, Rows updated: %s", kwargs['update'].rows_created, kwargs['update'].rows_updated)


    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_standard()

    def __str__(self):
        return str(self.key)


@receiver(models.signals.post_save, sender=DOBFiledPermit)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = sender.annotate_property_standard(
                instance.bbl.propertyannotation)
            annotation.save()
        except Exception as e:
            print(e)
