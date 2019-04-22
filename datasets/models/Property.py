from django.db import models
from django.db.models import Q, F, Count, Sum, Exists, OuterRef, Prefetch, FilteredRelation
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils.validation_filters import is_null, exceeds_char_length
from core.utils.transform import from_csv_file_to_gen, with_geo, get_geo
from core.utils.csv_helpers import extract_csvs_from_zip
from core.utils.address import clean_number_and_streets

from datasets import models as ds

import logging
from django.conf import settings
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
        rentstab_records = ds.RentStabilizationRecord.objects.only('ucbbl').filter(ucbbl=OuterRef('bbl'))
        return self.filter(unitsrentstabilized__gte=1).annotate(has_rentstab=Exists(rentstab_records)).filter(has_rentstab=True)

    def alternate_rentstab_filter(self):
        return self.filter(yearbuilt__lte=1974, yearbuilt__gte=1).annotate(rs_units=Sum('unitsrentstabilized')).filter(rs_units__gte=1)

    def rentreg_filter(self, program=None):
        corerecords = ds.CoreSubsidyRecord.objects.only('bbl').filter(bbl=OuterRef('bbl'))
        j51records = ds.SubsidyJ51.objects.only('bbl').filter(bbl=OuterRef('bbl'))
        subsidy421a = ds.Subsidy421a.objects.only('bbl').filter(bbl=OuterRef('bbl'))

        queryset = self.annotate(has_core=Exists(corerecords), has_subsidyj51=Exists(j51records), has_subsidy421a=Exists(
            subsidy421a)).filter(Q(has_core=True) | Q(has_subsidyj51=True) | Q(has_subsidy421a=True))

        # queryset = self.annotate(corerecords=Count('coresubsidyrecord'), subsidyj51records=Count('subsidyj51'), subsidy421arecords=Count(
        #     'subsidy421a')).filter(Q(corerecords__gte=1) | Q(subsidyj51records__gte=1) | Q(subsidy421arecords__gte=1))
        if program:
            return queryset.prefetch_related('coresubsidyrecord').filter(coresubsidyrecord__programname__icontains=program)
        else:
            return queryset

    def smallhome_filter(self, units=4):
        return self.filter(unitsres__gte=1, unitsres__lte=units)

    def marketrate_filter(self):
        rentstab_records = ds.RentStabilizationRecord.objects.only('ucbbl').filter(ucbbl=OuterRef('bbl'))
        corerecords = ds.CoreSubsidyRecord.objects.only('bbl').filter(bbl=OuterRef('bbl'))
        publichousingrecords = ds.PublicHousingRecord.objects.only('bbl').filter(bbl=OuterRef('bbl'))
        return self.annotate(
            has_rentstab=Exists(rentstab_records),
            has_core=Exists(corerecords),
            has_publichousing=Exists(publichousingrecords)
        ).filter(Q(
            has_core=False,
            has_publichousing=False,
            has_rentstab=False))

    def publichousing_filter(self):
        return self.annotate(publichousingrecords=Count('publichousingrecord')).filter(publichousingrecords__gte=1)

    def council(self, number):
        council_bbls = ds.Property.objects.filter(council=number).only('bbl')
        return self.filter(bbl__in=council_bbls)

    def community(self, number):
        community_bbls = ds.Property.objects.filter(cd=number).only('bbl')
        return self.filter(bbl__in=community_bbls)

    def residential(self):
        return self.filter(unitsres__gte=1)

    def rentstab(self):
        # return self.residential().rs_annotate().rentstab_filter()
        return self.rentstab_filter()

    def rentreg(self, program=None):
        return self.rentreg_filter(program)

    def smallhome(self, units=4):
        return self.smallhome_filter(units=units)

    def marketrate(self):
        return self.residential().marketrate_filter()

    def publichousing(self):
        return self.publichousing_filter()

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
        queryset = PropertyQuerySet(self.model, using=self._db)
        # queryset.annotate(acrisrealmaster_set=Prefetch('acrisreallegal', filter=))
        return queryset

    def council(self, number):
        return self.get_queryset().council(number)

    def community(self, number):
        return self.get_queryset().community(number)

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

    SHORT_SUMMARY_FIELDS = ('bbl', 'council', 'cd', 'yearbuilt', 'unitsres', 'unitsrentstabilized', 'unitstotal',
                            'bldgclass', 'zonedist1', 'numbldgs', 'numfloors', 'address', 'lat', 'lng',)

    current_version = '18V1'
    objects = PropertyManager()
    current = CurrentPropertyManager()
    obsolete = ObsoletePropertyManager()

    # https://www1.nyc.gov/assets/planning/download/pdf/data-maps/open-data/pluto_datadictionary.pdf?r=18v1
    bbl = models.CharField(primary_key=True, max_length=10, blank=False, null=False)
    council = models.ForeignKey('Council', on_delete=models.SET_NULL, null=True,
                                db_column='council', db_constraint=False)
    borough = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    cd = models.ForeignKey('Community', on_delete=models.SET_NULL, null=True,
                           db_column='cd', db_constraint=False)
    ct2010 = models.TextField(blank=True, null=True)
    cb2010 = models.TextField(blank=True, null=True)
    schooldist = models.SmallIntegerField(blank=True, null=True)
    zipcode = models.TextField(db_index=True, blank=True, null=True)
    firecomp = models.TextField(blank=True, null=True)
    policeprct = models.TextField(blank=True, null=True)
    healthcenterdistrict = models.SmallIntegerField(blank=True, null=True)
    healtharea = models.TextField(blank=True, null=True)
    sanitboro = models.TextField(blank=True, null=True)
    sanitdistrict = models.SmallIntegerField(blank=True, null=True)
    sanitsub = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
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
    mapplutof = models.TextField(blank=True, null=True)
    plutomapid = models.TextField(blank=True, null=True)
    firm07flag = models.TextField(blank=True, null=True)
    pfirm15flag = models.TextField(blank=True, null=True)
    rpaddate = models.DateTimeField(blank=True, null=True)
    dcasdate = models.DateTimeField(blank=True, null=True)
    zoningdate = models.DateTimeField(blank=True, null=True)
    landmkdate = models.DateTimeField(blank=True, null=True)
    basempdate = models.DateTimeField(blank=True, null=True)
    masdate = models.DateTimeField(blank=True, null=True)
    polidate = models.DateTimeField(blank=True, null=True)
    edesigdate = models.DateTimeField(blank=True, null=True)
    geom = models.TextField(blank=True, null=True)
    version = models.TextField(db_index=True, blank=True, null=True)
    # Custom fields
    lng = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    lat = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    unitsrentstabilized = models.IntegerField(blank=True, null=True)
    original_address = models.TextField(blank=True, null=True)

    def get_rentstabilized_units(self):
        try:
            return self.rentstabilizationrecord.get_latest_count()
        except Exception as e:
            return 0
    # trims down new update files to preserve memory
    # uses original header values

    @classmethod
    def recreate_community_relations(self):
        for property in self.objects.all():
            try:
                property.cd = ds.Community.objects.get(id=property.cd_id)
                property.save()
            except Exception as e:
                logger.debug('Unable to find community for {}'.format(property))

    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def pre_validation_filters(self, gen_rows):
        logger.debug("prevalidating properties")
        count = 0
        for row in gen_rows:
            row['original_address'] = row['address']
            row['address'] = clean_number_and_streets(row['address'], True)
            count = count + 1
            if count % settings.BATCH_SIZE == 0:
                logger.debug("cleaned {} properties".format(count))

            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(extract_csvs_from_zip(file_path), update))

    @classmethod
    def add_geometry(self):
        for record in self.objects.all():
            lng, lat = get_geo(record)
            record.lat = lat
            record.lng = lng
            record.save()

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.seed_with_upsert(**kwargs)
        logger.debug('adding geometry')
        self.add_geometry()

    def __str__(self):
        return str(self.bbl)
