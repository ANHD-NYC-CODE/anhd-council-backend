from django.db import models
from django.db.models import Q, F, Count, Exists, OuterRef, Prefetch
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils.validation_filters import is_null, exceeds_char_length
from core.utils.transform import from_csv_file_to_gen, with_geo
from core.utils.csv_helpers import extract_csvs_from_zip
from datasets import models as ds

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
        rentstab_records = ds.RentStabilizationRecord.objects.only('ucbbl', 'uc2007', 'uc2008', 'uc2009', 'uc2010', 'uc2011',
                                                                   'uc2012', 'uc2013', 'uc2014', 'uc2015', 'uc2016', 'uc2017', 'uc2018', 'uc2019', 'uc2020',).filter(ucbbl=OuterRef('bbl'))
        return self.filter(yearbuilt__lte=1974, yearbuilt__gte=1).annotate(has_rentstab=Exists(rentstab_records)).filter(has_rentstab=True)

    def rentreg_filter(self):
        return self.annotate(corerecords=Count('coresubsidyrecord'), subsidyj51records=Count('subsidyj51'), subsidy421arecords=Count('subsidy421a')).filter(Q(unitsres__gte=1), Q(corerecords__gte=1) | Q(subsidyj51records__gte=1) | Q(subsidy421arecords__gte=1))

    def smallhome_filter(self):
        return self.filter(unitsres__lte=4)

    def marketrate_filter(self):
        return self.annotate(
            publichousingcount=Count('publichousingrecord'),
            rentstabilizationrecord2007=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2007__gt=0)),
            rentstabilizationrecord2008=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2008__gt=0)),
            rentstabilizationrecord2009=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2009__gt=0)),
            rentstabilizationrecord2010=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2010__gt=0)),
            rentstabilizationrecord2011=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2011__gt=0)),
            rentstabilizationrecord2012=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2012__gt=0)),
            rentstabilizationrecord2013=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2013__gt=0)),
            rentstabilizationrecord2014=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2014__gt=0)),
            rentstabilizationrecord2015=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2015__gt=0)),
            rentstabilizationrecord2016=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2016__gt=0)),
            rentstabilizationrecord2017=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2017__gt=0)),
            rentstabilizationrecord2018=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2018__gt=0)),
            rentstabilizationrecord2019=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2019__gt=0)),
            rentstabilizationrecord2020=Count('rentstabilizationrecord',
                                              filter=Q(rentstabilizationrecord__uc2020__gt=0))
        ).filter(Q(
            unitsres__gte=6,
            publichousingcount=0,
            rentstabilizationrecord2007=0,
            rentstabilizationrecord2008=0,
            rentstabilizationrecord2009=0,
            rentstabilizationrecord2010=0,
            rentstabilizationrecord2011=0,
            rentstabilizationrecord2012=0,
            rentstabilizationrecord2013=0,
            rentstabilizationrecord2014=0,
            rentstabilizationrecord2015=0,
            rentstabilizationrecord2016=0,
            rentstabilizationrecord2017=0,
            rentstabilizationrecord2018=0,
            rentstabilizationrecord2019=0,
            rentstabilizationrecord2020=0) | Q(unitsres__lte=5))

    def publichousing_filter(self):
        return self.annotate(publichousingrecords=Count('publichousingrecord')).filter(publichousingrecords__gte=1)

    def council(self, number):
        return self.filter(council=number)

    def residential(self):
        return self.filter(unitsres__gte=1)

    def rentstab(self):
        return self.residential().rentstab_filter()

    def rentreg(self):
        return self.residential().rentreg_filter()

    def smallhome(self):
        return self.residential().smallhome_filter()

    def marketrate(self):
        return self.residential().marketrate_filter()

    def publichousing(self):
        return self.residential().publichousing_filter()

    def annotate_all(self):
        return self.annotate(hpdcomplaints__count=Count('hpdcomplaint', distinct=True), hpdviolations__count=Count('hpdviolation', distinct=True), dobviolations__count=Count('dobviolation', distinct=True), ecbviolations__count=Count('ecbviolation', distinct=True))

    def rs_annotate(self):
        return self.annotate(
            rentstabilizationrecord2007=F('rentstabilizationrecord__uc2007'),
            rentstabilizationrecord2008=F('rentstabilizationrecord__uc2008'),
            rentstabilizationrecord2009=F('rentstabilizationrecord__uc2009'),
            rentstabilizationrecord2010=F('rentstabilizationrecord__uc2010'),
            rentstabilizationrecord2011=F('rentstabilizationrecord__uc2011'),
            rentstabilizationrecord2012=F('rentstabilizationrecord__uc2012'),
            rentstabilizationrecord2013=F('rentstabilizationrecord__uc2013'),
            rentstabilizationrecord2014=F('rentstabilizationrecord__uc2014'),
            rentstabilizationrecord2015=F('rentstabilizationrecord__uc2015'),
            rentstabilizationrecord2016=F('rentstabilizationrecord__uc2016'),
            rentstabilizationrecord2017=F('rentstabilizationrecord__uc2017'),
            rentstabilizationrecord2018=F('rentstabilizationrecord__uc2018'),
            rentstabilizationrecord2019=F('rentstabilizationrecord__uc2019'),
            rentstabilizationrecord2020=F('rentstabilizationrecord__uc2020'))

        return self


class PropertyManager(models.Manager):
    def get_queryset(self):
        return PropertyQuerySet(self.model, using=self._db)

    def council(self, number):
        return self.get_queryset().council(number)

    def residential(self):
        return self.get_queryset().residential()

    def rentstab(self):
        return self.get_queryset().rentstab().residential()

    def rentreg(self):
        return self.get_queryset().rentreg().residential()

    def smallhome(self):
        return self.get_queryset().smallhome().residential()

    def marketrate(self):
        return self.get_queryset().marketrate().residential()

    def publichousing(self):
        return self.get_queryset().publichousing().residential()


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
