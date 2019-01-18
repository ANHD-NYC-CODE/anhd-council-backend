from django.db import models
from django.db.models import Q, F, Count
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils.validation_filters import is_null, exceeds_char_length
from core.utils.transform import from_csv_file_to_gen, with_geo
from core.utils.csv_helpers import extract_csvs_from_zip
import logging

logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Upsert
#
# Download latest .csv zipfile from:
# https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page
# upload zipfile file through admin, update


class CurrentPropertyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(version=self.model.current_version)


class ObsoletePropertyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(~Q(version=self.model.current_version))


class PropertyQuerySet(models.QuerySet):
    def rentstab_filter(self):
        return self.filter(yearbuilt__lte=1974, yearbuilt__gte=1).annotate(rentstabrecords=Count('rentstabilizationrecord')).filter(rentstabrecords__gte=1)

    def rentreg_filter(self):
        return self.annotate(corerecords=Count('coresubsidyrecord'), subsidyj51records=Count('subsidyj51'), subsidy421arecords=Count('subsidy421a')).filter(Q(corerecords__gte=1) | Q(subsidyj51records__gte=1) | Q(subsidy421arecords__gte=1))

    def smallhome_filter(self):
        return self.filter(unitsres__lte=4)

    def marketrate_filter(self):
        return self.annotate(
            rs2007=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2007__gt=0)),
            rs2008=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2008__gt=0)),
            rs2009=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2009__gt=0)),
            rs2010=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2010__gt=0)),
            rs2011=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2011__gt=0)),
            rs2012=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2012__gt=0)),
            rs2013=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2013__gt=0)),
            rs2014=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2014__gt=0)),
            rs2015=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2015__gt=0)),
            rs2016=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2016__gt=0)),
            rs2017=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2017__gt=0)),
            rs2018=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2018__gt=0)),
            rs2019=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2019__gt=0)),
            rs2020=Count('rentstabilizationrecord', filter=Q(rentstabilizationrecord__uc2020__gt=0))
        ).filter(Q(
            unitsres__gte=6,
            rs2007=0,
            rs2008=0,
            rs2009=0,
            rs2010=0,
            rs2011=0,
            rs2012=0,
            rs2013=0,
            rs2014=0,
            rs2015=0,
            rs2016=0,
            rs2017=0,
            rs2018=0,
            rs2019=0,
            rs2020=0) | Q(unitsres__lte=5))

    def council(self, number):
        return self.filter(council=number)

    def residential(self):
        return self.filter(unitsres__gt=0)

    def rentstab(self):
        return self.residential().rentstab_filter()

    def rentreg(self):
        return self.residential().rentreg_filter()

    def smallhome(self):
        return self.residential().smallhome_filter()

    def marketrate(self):
        return self.residential().marketrate_filter()

    def rentstab_annotate(self, fields_list):
        unique_fields_list = []
        for field in fields_list:
            unique_fields_list.append(field.split('__')[0])
        unique_fields_list = list(set(unique_fields_list))

        for field in unique_fields_list:
            if field == 'hpdcomplaint':
                self = self.annotate(hpdcomplaint_count=Count(field))
            if field == 'hpdviolation':
                self = self.annotate(hpdviolation_count=Count(field))
            if field == 'dobcomplaint':
                import pdb
                pdb.set_trace()
                self = self.annotate(dobcomplaint_count=Count(field))
            if field == 'dobviolation':
                self = self.annotate(dobviolation_count=Count(field))
            if field == 'ecbviolation':
                self = self.annotate(ecbviolation_count=Count(field))
            if field == 'permitsissued':
                self = self.annotate(permitsissued_count=Count('dobpermitissuedlegacy') + Count('dobpermitissuednow'))
            # if field == 'acris':
            #     self = self.annotate(acris_count=Count('acrisreallegal'))
            if field == 'rentstab':
                self = self.annotate(
                    rs2007=F('rentstabilizationrecord__uc2007'),
                    rs2008=F('rentstabilizationrecord__uc2008'),
                    rs2009=F('rentstabilizationrecord__uc2009'),
                    rs2010=F('rentstabilizationrecord__uc2010'),
                    rs2011=F('rentstabilizationrecord__uc2011'),
                    rs2012=F('rentstabilizationrecord__uc2012'),
                    rs2013=F('rentstabilizationrecord__uc2013'),
                    rs2014=F('rentstabilizationrecord__uc2014'),
                    rs2015=F('rentstabilizationrecord__uc2015'),
                    rs2016=F('rentstabilizationrecord__uc2016'),
                    rs2017=F('rentstabilizationrecord__uc2017'),
                    rs2018=F('rentstabilizationrecord__uc2018'),
                    rs2019=F('rentstabilizationrecord__uc2019'),
                    rs2020=F('rentstabilizationrecord__uc2020'))

        return self


class PropertyManager(models.Manager):
    def get_queryset(self):
        return PropertyQuerySet(self.model, using=self._db)

    def council(self, number):
        return self.get_queryset().council(number)

    def residential(self):
        return self.get_queryset().residential()

    def rentstab(self):
        return self.get_queryset().renstab()

    def rentreg(self):
        return self.get_queryset().rentreg()

    def smallhome(self):
        return self.get_queryset().smallhome()

    def marketrate(self):
        return self.get_queryset().marketrate()


class Property(BaseDatasetModel, models.Model):
    current_version = '18V1'
    objects = PropertyManager()
    current = CurrentPropertyManager()
    obsolete = ObsoletePropertyManager()

    # 763178 +- records for residential properties.
    # Current version: Pluto18v1
    # To update to latest Pluto version,
    # Compare the columns between the next Pluto version and this.
    # Add, but do not delete any columns if different.
    # Create a django migration to add new columns.
    # Create an Update with the latest pluto zip file in admin panel.
    # Existing properties will be overritten with latest values.
    # New properties will be added.
    # Old properties will not be removed automatically, need manual removal.
    # Property.obsolete.all().delete()
    bbl = models.CharField(primary_key=True, max_length=10, blank=False, null=False)
    council = models.ForeignKey('Council', on_delete=models.SET_NULL, null=True,
                                db_column='council', db_constraint=False)
    borough = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    cd = models.SmallIntegerField(blank=True, null=True)
    ct2010 = models.TextField(blank=True, null=True)
    cb2010 = models.TextField(blank=True, null=True)
    schooldist = models.SmallIntegerField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    firecomp = models.TextField(blank=True, null=True)
    policeprct = models.TextField(blank=True, null=True)
    healthcenterdistrict = models.SmallIntegerField(blank=True, null=True)
    healtharea = models.TextField(blank=True, null=True)
    sanitboro = models.TextField(blank=True, null=True)
    sanitdistrict = models.SmallIntegerField(blank=True, null=True)
    sanitsub = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    original_address = models.TextField(blank=True, null=True)
    zonedist1 = models.TextField(blank=True, null=True)
    zonedist2 = models.TextField(blank=True, null=True)
    zonedist3 = models.TextField(blank=True, null=True)
    zonedist4 = models.TextField(blank=True, null=True)
    overlay1 = models.TextField(blank=True, null=True)
    overlay2 = models.TextField(blank=True, null=True)
    spdist1 = models.TextField(blank=True, null=True)
    spdist2 = models.TextField(blank=True, null=True)
    spdist3 = models.TextField(blank=True, null=True)
    ltdheight = models.TextField(blank=True, null=True)
    splitzone = models.BooleanField(blank=True, null=True)
    bldgclass = models.TextField(db_index=True, blank=True, null=True)
    landuse = models.SmallIntegerField(blank=True, null=True)
    easements = models.TextField(blank=True, null=True)
    ownertype = models.TextField(blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    lotarea = models.BigIntegerField(blank=True, null=True)
    bldgarea = models.BigIntegerField(blank=True, null=True)
    comarea = models.BigIntegerField(blank=True, null=True)
    resarea = models.BigIntegerField(blank=True, null=True)
    officearea = models.BigIntegerField(blank=True, null=True)
    retailarea = models.BigIntegerField(blank=True, null=True)
    garagearea = models.BigIntegerField(blank=True, null=True)
    strgearea = models.BigIntegerField(blank=True, null=True)
    factryarea = models.BigIntegerField(blank=True, null=True)
    otherarea = models.BigIntegerField(blank=True, null=True)
    areasource = models.TextField(blank=True, null=True)
    numbldgs = models.IntegerField(db_index=True, blank=True, null=True)
    numfloors = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    unitsres = models.IntegerField(db_index=True, blank=True, null=True)
    unitstotal = models.IntegerField(db_index=True, blank=True, null=True)
    lotfront = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    lotdepth = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    bldgfront = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    bldgdepth = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    ext = models.TextField(blank=True, null=True)
    proxcode = models.TextField(blank=True, null=True)
    irrlotcode = models.BooleanField(blank=True, null=True)
    lottype = models.TextField(blank=True, null=True)
    bsmtcode = models.TextField(blank=True, null=True)
    assessland = models.BigIntegerField(blank=True, null=True)
    assesstot = models.BigIntegerField(blank=True, null=True)
    exemptland = models.BigIntegerField(blank=True, null=True)
    exempttot = models.BigIntegerField(blank=True, null=True)
    yearbuilt = models.SmallIntegerField(db_index=True, blank=True, null=True)
    yearalter1 = models.SmallIntegerField(blank=True, null=True)
    yearalter2 = models.SmallIntegerField(blank=True, null=True)
    histdist = models.TextField(blank=True, null=True)
    landmark = models.TextField(blank=True, null=True)
    builtfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    residfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    commfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    facilfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    borocode = models.TextField(db_index=True, blank=True, null=True)
    condono = models.TextField(blank=True, null=True)
    tract2010 = models.TextField(blank=True, null=True)
    xcoord = models.IntegerField(blank=True, null=True)
    ycoord = models.IntegerField(blank=True, null=True)
    zonemap = models.TextField(blank=True, null=True)
    zmcode = models.TextField(blank=True, null=True)
    sanborn = models.TextField(blank=True, null=True)
    taxmap = models.TextField(blank=True, null=True)
    edesignum = models.TextField(blank=True, null=True)
    appbbl = models.TextField(db_index=True,  blank=True, null=True)
    appdate = models.DateTimeField(blank=True, null=True)
    plutomapid = models.TextField(blank=True, null=True)
    firm07flag = models.TextField(blank=True, null=True)
    pfirm15flag = models.TextField(blank=True, null=True)
    version = models.TextField(db_index=True, blank=True, null=True)
    lng = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    lat = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['bbl']) or exceeds_char_length(row['bbl'], 10):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_geo(from_csv_file_to_gen(extract_csvs_from_zip(file_path), update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.bulk_seed(**kwargs)

    def __str__(self):
        return self.bbl
