from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_xlsx_file_to_gen
from core.utils.database import execute

from datasets import models as ds


import logging
logger = logging.getLogger('app')

# Instructions:
# 1) Login to PropertyShark on 1st of month & download last month's data for "PreForeclosure"
# 2) Upload via admin interface


class PSPreForeclosure(BaseDatasetModel, models.Model):
    QUERY_DATE_KEY = 'dateadded'
    RECENT_DATE_PINNED = True

    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-dateadded']),
            models.Index(fields=['-dateadded']),
        ]

    key = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)

    address = models.TextField(blank=True, null=True)  # address
    indexno = models.TextField(blank=True, null=True)  # index
    zipcode = models.TextField(blank=True, null=True)
    creditor = models.TextField(blank=True, null=True)  # creditor
    neighborhood = models.TextField(blank=True, null=True)
    documenttype = models.TextField(blank=True, null=True)  # document_type
    schooldistrict = models.TextField(blank=True, null=True)
    lientype = models.TextField(blank=True, null=True)  # lien_type
    buildingclass = models.TextField(blank=True, null=True)
    taxvalue = models.TextField(blank=True, null=True)
    dateadded = models.DateTimeField(blank=True, null=True)  # date_added
    bldgareasqft = models.IntegerField(blank=True, null=True)
    debtor = models.TextField(blank=True, null=True)  # debtor
    debtoraddress = models.TextField(blank=True, null=True)
    mortgagedate = models.DateTimeField(blank=True, null=True)  # mortgage_date
    mortgageamount = models.IntegerField(blank=True, null=True)  # mortgage_amount
    hasphoto = models.TextField(blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            row['key'] = "#{}-#{}-#{}".format(row['indexno'], row['bbl'], row['documenttype'])
            row['bbl'] = row['bbl'].replace('-', '')
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_xlsx_file_to_gen(file_path, 'Pre-Foreclosures Details', update, skip_rows=7))

    @classmethod
    def upsert_sql(self, other_table, cols):
        table_name = ds.Foreclosure._meta.db_table
        primary_key = ds.Foreclosure._meta.pk.name
        other_table_name = other_table._meta.db_table
        fields = ', '.join([k.name for k in ds.Foreclosure._meta.get_fields()])
        upsert_fields = ', '.join([k.name + "=EXCLUDED." + k.name for k in ds.Foreclosure._meta.get_fields()])

        sql = "INSERT INTO {table_name} ({fields}) SELECT {cols} FROM {other_table_name} ON CONFLICT ({primary_key}) DO UPDATE SET {upsert_fields};"
        return sql.format(table_name=table_name, fields=fields, cols=cols, other_table_name=other_table_name, primary_key=primary_key, upsert_fields=upsert_fields)

    @classmethod
    def update_foreclosure_table(self, **kwargs):
        logger.debug("Seeding/Updating {}", ds.Foreclosure.__name__)
        # Add records from both tables
        preforeclosure_table = ds.PSPreForeclosure
        preforeclosure_count = preforeclosure_table.objects.count()
        preforeclosure_cols = "concat({other_table_name}.indexno, {other_table_name}.bbl), {other_table_name}.bbl, {other_table_name}.indexno, {other_table_name}.address, {other_table_name}.documenttype, {other_table_name}.lientype, {other_table_name}.dateadded, {other_table_name}.creditor, {other_table_name}.debtor, {other_table_name}.mortgagedate, {other_table_name}.mortgageamount, NULL, {other_table_name}.key, \'PropertyShark\'".format(
            other_table_name=preforeclosure_table._meta.db_table, other_model_name=preforeclosure_table._meta.model_name)

        execute(self.upsert_sql(preforeclosure_table, preforeclosure_cols))
        logger.debug("Completed seed into {} for {}", ds.Foreclosure.__name__, preforeclosure_table._meta.db_table)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        self.seed_with_upsert(**kwargs)
        self.update_foreclosure_table(**kwargs)
        ds.Foreclosure.annotate_properties()

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_month_offset()
