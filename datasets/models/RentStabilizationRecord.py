from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets import models as ds
import logging
import datetime
from django.dispatch import receiver

logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Overwrite
#
# Download file from:
# http://taxbills.nyc/joined.csv
# upload file through admin then update
# When updating new year, will likely have to add new key to dictionary below for model for that new year.

class RentStabilizationRecord(BaseDatasetModel, models.Model):
    download_endpoint = "http://taxbills.nyc/joined.csv"
    data_2018 = "https://s3.amazonaws.com/justfix-data/rentstab_counts_for_pluto_19v1_bbls.csv"
    MANUAL_YEAR = 2023  # This is likely no longer being used.

    class Meta:
        indexes = [
            models.Index(fields=['ucbbl', 'uc2007']),
            models.Index(fields=['ucbbl', 'uc2008']),
            models.Index(fields=['ucbbl', 'uc2009']),
            models.Index(fields=['ucbbl', 'uc2010']),
            models.Index(fields=['ucbbl', 'uc2011']),
            models.Index(fields=['ucbbl', 'uc2012']),
            models.Index(fields=['ucbbl', 'uc2013']),
            models.Index(fields=['ucbbl', 'uc2014']),
            models.Index(fields=['ucbbl', 'uc2015']),
            models.Index(fields=['ucbbl', 'uc2016']),
            models.Index(fields=['ucbbl', 'uc2017']),
            models.Index(fields=['ucbbl', 'uc2018']),
            models.Index(fields=['ucbbl', 'uc2019']),
            models.Index(fields=['ucbbl', 'uc2020']),
            models.Index(fields=['ucbbl', 'uc2021']),
            models.Index(fields=['ucbbl', 'uc2022']),
            models.Index(fields=['ucbbl', 'uc2023']),
            models.Index(fields=['ucbbl', 'uc2024']),
            models.Index(fields=['uc2007', 'ucbbl']),
            models.Index(fields=['uc2008', 'ucbbl']),
            models.Index(fields=['uc2009', 'ucbbl']),
            models.Index(fields=['uc2010', 'ucbbl']),
            models.Index(fields=['uc2011', 'ucbbl']),
            models.Index(fields=['uc2012', 'ucbbl']),
            models.Index(fields=['uc2013', 'ucbbl']),
            models.Index(fields=['uc2014', 'ucbbl']),
            models.Index(fields=['uc2015', 'ucbbl']),
            models.Index(fields=['uc2016', 'ucbbl']),
            models.Index(fields=['uc2017', 'ucbbl']),
            models.Index(fields=['uc2018', 'ucbbl']),
            models.Index(fields=['uc2019', 'ucbbl']),
            models.Index(fields=['uc2020', 'ucbbl']),
            models.Index(fields=['uc2021', 'ucbbl']),
            models.Index(fields=['uc2022', 'ucbbl']),
            models.Index(fields=['uc2023', 'ucbbl']),
            models.Index(fields=['uc2024', 'ucbbl']),
        ]
    id = models.TextField(primary_key=True, blank=False, null=False)
    ucbbl = models.OneToOneField('Property', db_column='ucbbl', db_constraint=False,
                                 on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    uc2007 = models.IntegerField(db_index=True, blank=True, null=True)
    est2007 = models.BooleanField(blank=True, null=True)
    dhcr2007 = models.BooleanField(blank=True, null=True)
    abat2007 = models.TextField(blank=True, null=True)
    uc2008 = models.IntegerField(db_index=True, blank=True, null=True)
    est2008 = models.BooleanField(blank=True, null=True)
    dhcr2008 = models.BooleanField(blank=True, null=True)
    abat2008 = models.TextField(blank=True, null=True)
    uc2009 = models.IntegerField(db_index=True, blank=True, null=True)
    est2009 = models.BooleanField(blank=True, null=True)
    dhcr2009 = models.BooleanField(blank=True, null=True)
    abat2009 = models.TextField(blank=True, null=True)
    uc2010 = models.IntegerField(db_index=True, blank=True, null=True)
    est2010 = models.BooleanField(blank=True, null=True)
    dhcr2010 = models.BooleanField(blank=True, null=True)
    abat2010 = models.TextField(blank=True, null=True)
    uc2011 = models.IntegerField(db_index=True, blank=True, null=True)
    est2011 = models.BooleanField(blank=True, null=True)
    dhcr2011 = models.BooleanField(blank=True, null=True)
    abat2011 = models.TextField(blank=True, null=True)
    uc2012 = models.IntegerField(db_index=True, blank=True, null=True)
    est2012 = models.BooleanField(blank=True, null=True)
    dhcr2012 = models.BooleanField(blank=True, null=True)
    abat2012 = models.TextField(blank=True, null=True)
    uc2013 = models.IntegerField(db_index=True, blank=True, null=True)
    est2013 = models.BooleanField(blank=True, null=True)
    dhcr2013 = models.BooleanField(blank=True, null=True)
    abat2013 = models.TextField(blank=True, null=True)
    uc2014 = models.IntegerField(db_index=True, blank=True, null=True)
    est2014 = models.BooleanField(blank=True, null=True)
    dhcr2014 = models.BooleanField(blank=True, null=True)
    abat2014 = models.TextField(blank=True, null=True)
    uc2015 = models.IntegerField(db_index=True, blank=True, null=True)
    est2015 = models.BooleanField(blank=True, null=True)
    dhcr2015 = models.BooleanField(blank=True, null=True)
    abat2015 = models.TextField(blank=True, null=True)
    uc2016 = models.IntegerField(db_index=True, blank=True, null=True)
    est2016 = models.BooleanField(blank=True, null=True)
    dhcr2016 = models.BooleanField(blank=True, null=True)
    abat2016 = models.TextField(blank=True, null=True)
    uc2017 = models.IntegerField(db_index=True, blank=True, null=True)
    est2017 = models.BooleanField(blank=True, null=True)
    dhcr2017 = models.BooleanField(blank=True, null=True)
    abat2017 = models.TextField(blank=True, null=True)
    uc2018 = models.IntegerField(db_index=True, blank=True, null=True)
    est2018 = models.BooleanField(blank=True, null=True)
    dhcr2018 = models.BooleanField(blank=True, null=True)
    abat2018 = models.TextField(blank=True, null=True)
    uc2019 = models.IntegerField(db_index=True, blank=True, null=True)
    est2019 = models.BooleanField(blank=True, null=True)
    dhcr2019 = models.BooleanField(blank=True, null=True)
    abat2019 = models.TextField(blank=True, null=True)
    uc2020 = models.IntegerField(db_index=True, blank=True, null=True)
    est2020 = models.BooleanField(blank=True, null=True)
    dhcr2020 = models.BooleanField(blank=True, null=True)
    abat2020 = models.TextField(blank=True, null=True)
    uc2021 = models.IntegerField(db_index=True, blank=True, null=True)
    est2021 = models.BooleanField(blank=True, null=True)
    dhcr2021 = models.BooleanField(blank=True, null=True)
    abat2021 = models.TextField(blank=True, null=True)
    uc2022 = models.IntegerField(db_index=True, blank=True, null=True)
    est2022 = models.BooleanField(blank=True, null=True)
    dhcr2022 = models.BooleanField(blank=True, null=True)
    abat2022 = models.TextField(blank=True, null=True)
    uc2023 = models.IntegerField(db_index=True, blank=True, null=True)
    est2023 = models.BooleanField(blank=True, null=True)
    dhcr2023 = models.BooleanField(blank=True, null=True)
    abat2023 = models.TextField(blank=True, null=True)
    uc2024 = models.IntegerField(db_index=True, blank=True, null=True)
    est2024 = models.BooleanField(blank=True, null=True)
    dhcr2024 = models.BooleanField(blank=True, null=True)
    abat2024 = models.TextField(blank=True, null=True)
    cd = models.SmallIntegerField(blank=True, null=True)
    ct2010 = models.TextField(blank=True, null=True)
    cb2010 = models.TextField(blank=True, null=True)
    council = models.IntegerField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    numbldgs = models.SmallIntegerField(blank=True, null=True)
    numfloors = models.DecimalField(
        decimal_places=2, max_digits=8, blank=True, null=True)
    unitsres = models.IntegerField(blank=True, null=True)
    unitstotal = models.IntegerField(blank=True, null=True)
    yearbuilt = models.SmallIntegerField(blank=True, null=True)
    condono = models.SmallIntegerField(blank=True, null=True)
    lon = models.DecimalField(
        decimal_places=16, max_digits=32, blank=True, null=True)
    lat = models.DecimalField(
        decimal_places=16, max_digits=32, blank=True, null=True)
    pdfsoa2018 = models.TextField(default='', blank=True, null=True)
    pdfsoa2019 = models.TextField(default='', blank=True, null=True)
    # holds the latest uc value from the latest year w value
    latestuctotals = models.IntegerField(blank=True, null=True)

    def get_latest_count(self):
        # Get all available 'uc' columns dynamically
        uc_columns = sorted(
            [int(field.name.replace('uc', '')) for field in self._meta.fields if field.name.startswith('uc')],
            reverse=True  # Start from the highest year
        )
    
        for year in uc_columns:
            latest_count = getattr(self, f'uc{year}', None)
            if latest_count is not None:  # ✅ Return first non-null value
                return latest_count
    
        return 0  # ✅ Default to 0 if all values are null

    def get_earliest_count(self):
        # Get all available 'uc' columns dynamically and filter to years >= 2007
        uc_columns = sorted(
            [int(field.name.replace('uc', '')) for field in self._meta.fields if field.name.startswith('uc')]
        )
    
        for year in uc_columns:
            if year >= 2007:  # ✅ Ensure it starts at 2007
                earliest_count = getattr(self, f'uc{year}', None)
                if earliest_count is not None:  # ✅ Return first non-null value
                    return earliest_count
    
        return 0  # ✅ Default to 0 if all values are null


    def get_percent_lost(self):
        # returns negative number for loss
        # positive number for gain
        try:
            difference = self.get_earliest_count() - self.get_latest_count()
            if (difference >= 0):
                return -(difference / self.get_earliest_count())
            else:
                return (-difference / self.get_earliest_count())

        except Exception as e:
            return 0

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['ucbbl']):
                continue  # ❌ Skipping could cause missing records
    
            row['ucbbl'] = str(row['ucbbl'])
            row['id'] = row['ucbbl']
    
            # ❌ Might fail to assign 'latestuctotals'
            year_cursor = self.MANUAL_YEAR
            while 'latestuctotals' not in row and year_cursor > 2006:
                key = f"uc{year_cursor}"
                if key in row and row[key] is not None:
                    row['latestuctotals'] = row[key]
                year_cursor -= 1
    
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        update = self.seed_with_upsert(**kwargs)
        return update

    @classmethod
    def annotate_properties(self):
        count = 0
        for annotation in ds.PropertyAnnotation.objects.filter(bbl__rentstabilizationrecord__isnull=False):
            try:
                annotation.unitsrentstabilized = annotation.bbl.get_rentstabilized_units()
                annotation.save()
                if count % 10000 == 0:
                    logger.debug('{} annotation: {}'.format(
                        self.__name__, count))
                count = count + 1
            except Exception as e:
                continue

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=RentStabilizationRecord)
def annotate_property_on_save(sender, instance, **kwargs):
    try:
        annotation = instance.ucbbl.propertyannotation
        old_value = annotation.unitsrentstabilized
        annotation.unitsrentstabilized = instance.get_rentstabilized_units()
        annotation.save()
        logger.info(f"Updated annotation for {instance.id} from {old_value} to {annotation.unitsrentstabilized}")
    except Exception as e:
        logger.error(f"Annotation failed for {instance.id}: {e}")
