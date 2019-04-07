from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, does_not_contain_values
from core.utils.database import execute
from datasets import models as ds
import logging

logger = logging.getLogger('app')

# Update process: Automatic
# Update strategy: Overwrite
#

# Create an update in admin with this model name, no file.

# TODO rename to DOBPermitIssued


class DOBFiledPermit(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', 'datefiled']),
            models.Index(fields=['datefiled', 'bbl']),

        ]

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
    jobtype = models.TextField(blank=True, null=True)  # no NOW equivalent
    jobdescription = models.TextField(blank=True, null=True)  # no NOW equivalent
    datefiled = models.DateTimeField(db_index=True, blank=True, null=True)  # no NOW equivalent
    applicantsfirstname = models.TextField(blank=True, null=True)
    applicantslastname = models.TextField(blank=True, null=True)
    applicantprofessionaltitle = models.TextField(blank=True, null=True)
    applicantlicense = models.TextField(blank=True, null=True)
    ownerbusinessname = models.TextField(blank=True, null=True)
    initialcost = models.IntegerField(blank=True, null=True)
    foreign_key = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)

    slim_query_fields = ["id", "bbl", "datefiled"]

    @classmethod
    def upsert_permit_sql(self, other_table, cols):
        table_name = self._meta.db_table
        primary_key = self._meta.pk.name
        other_table_name = other_table._meta.db_table
        fields = ', '.join([k.name for k in self._meta.get_fields()])
        upsert_fields = ', '.join([k.name + "=EXCLUDED." + k.name for k in self._meta.get_fields()])

        sql = "INSERT INTO {table_name} ({fields}) SELECT {cols} FROM {other_table_name} ON CONFLICT ({primary_key}) DO UPDATE SET {upsert_fields};"
        return sql.format(table_name=table_name, fields=fields, cols=cols, other_table_name=other_table_name, primary_key=primary_key, upsert_fields=upsert_fields)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        # Add records from both tables
        legacy_table = ds.DOBLegacyFiledPermit
        legacy_count = legacy_table.objects.count()
        legacy_cols = "concat(CAST({other_table_name}.jobs1no AS text), {other_table_name}.job), {other_table_name}.job, {other_table_name}.bbl, {other_table_name}.bin, {other_table_name}.house, {other_table_name}.streetname, {other_table_name}.borough, {other_table_name}.jobstatus, {other_table_name}.jobtype, {other_table_name}.jobdescription, {other_table_name}.prefilingdate, {other_table_name}.applicantsfirstname, {other_table_name}.applicantslastname, {other_table_name}.applicantprofessionaltitle, {other_table_name}.applicantlicense, {other_table_name}.ownersbusinessname, CAST({other_table_name}.initialcost AS int), CAST({other_table_name}.id AS text), \'{other_model_name}\'".format(
            other_table_name=legacy_table._meta.db_table, other_model_name=legacy_table._meta.model_name)

        now_table = ds.DOBNowFiledPermit
        now_count = now_table.objects.count()
        now_cols = "{other_table_name}.jobfilingnumber, {other_table_name}.jobfilingnumber, {other_table_name}.bbl, {other_table_name}.bin, {other_table_name}.houseno, {other_table_name}.streetname, {other_table_name}.borough, {other_table_name}.filingstatus, NULL, NULL, NULL, {other_table_name}.applicantfirstname, {other_table_name}.applicantlastname, {other_table_name}.applicantprofessionaltitle, {other_table_name}.applicantlicense, {other_table_name}.ownersbusinessname, CAST({other_table_name}.initialcost AS int), CAST({other_table_name}.id AS text), \'{other_model_name}\'".format(
            nil={None}, other_table_name=now_table._meta.db_table, other_model_name=now_table._meta.model_name)

        kwargs['update'].total_rows = legacy_count + now_count
        kwargs['update'].save()
        starting_count = self.objects.count()

        execute(self.upsert_permit_sql(legacy_table, legacy_cols))
        rows_created_legacy = self.objects.count() - starting_count
        kwargs['update'].rows_created = kwargs['update'].rows_created + rows_created_legacy
        kwargs['update'].rows_updated = kwargs['update'].rows_updated + (legacy_count - rows_created_legacy)
        kwargs['update'].save()
        logger.debug("Completed seed into {} for {}", self.__name__, legacy_table._meta.db_table)

        starting_count = self.objects.count()
        execute(self.upsert_permit_sql(now_table, now_cols))
        rows_created_now = self.objects.count() - starting_count
        kwargs['update'].rows_created = kwargs['update'].rows_created + rows_created_now
        kwargs['update'].rows_updated = kwargs['update'].rows_updated + (now_count - rows_created_now)
        kwargs['update'].save()

        logger.debug("Completed seed into {} for {}", self.__name__, now_table._meta.db_table)

    def __str__(self):
        return str(self.id)
