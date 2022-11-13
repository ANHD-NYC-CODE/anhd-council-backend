import json
from shapely.geometry import shape, Point

from django.db import models
from django.db.models import Q, F, Count, Sum, Exists, OuterRef, Prefetch, FilteredRelation
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils.validation_filters import is_null, exceeds_char_length
from core.utils.transform import from_csv_file_to_gen, with_geo, get_geo
from core.utils.csv_helpers import extract_csvs_from_zip
from core.utils.address import clean_number_and_streets
from django.dispatch import receiver
from core.utils.database import queryset_foreach
from core.utils.database import Status, progress_callback
from core.tasks import async_download_and_update

from datasets import models as ds

import logging
from django.conf import settings
logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Upsert
#
# Download latest Pluto .csv zipfile from:
# https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page
# upload zipfile file through admin, update
# *** Add the pluto version to the 'version' field in admin ****
# Ex: 20v6
# ** RESOURCE INTENSIVE UPDATE ** - don't run during regular updates after 7pm


class CurrentPropertyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(version=self.model.current_version)


class ObsoletePropertyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(~Q(version=self.model.current_version))


class PropertyQuerySet(models.QuerySet):
    def rentstab_filter(self):
        # rentstab_records = ds.RentStabilizationRecord.objects.only('ucbbl').filter(ucbbl=OuterRef('bbl'))

        # return self.filter(propertyannotation__unitsrentstabilized__gte=1).annotate(has_rentstab=Exists(rentstab_records)).filter(has_rentstab=True)
        return self.filter(propertyannotation__unitsrentstabilized__gte=1)

    def alternate_rentstab_filter(self):
        return self.filter(yearbuilt__lte=1974, yearbuilt__gte=1).annotate(rs_units=Sum('propertyannotation__unitsrentstabilized')).filter(rs_units__gte=1)

    def rentreg_filter(self, program=None):
        corerecords = ds.CoreSubsidyRecord.objects.only(
            'bbl').filter(bbl=OuterRef('bbl'))
        j51records = ds.SubsidyJ51.objects.only(
            'bbl').filter(bbl=OuterRef('bbl'))
        subsidy421a = ds.Subsidy421a.objects.only(
            'bbl').filter(bbl=OuterRef('bbl'))

        queryset = self.annotate(has_core=Exists(corerecords), has_subsidyj51=Exists(j51records), has_subsidy421a=Exists(
            subsidy421a)).filter(Q(has_core=True) | Q(has_subsidyj51=True) | Q(has_subsidy421a=True))

        if program:
            return queryset.prefetch_related('coresubsidyrecord').filter(subsidyprograms__programname__icontains=program)
        else:
            return queryset

    def smallhome_filter(self, units=4):
        return self.filter(unitsres__gte=1, unitsres__lte=units)

    def marketrate_filter(self):
        rentstab_records = ds.RentStabilizationRecord.objects.only(
            'ucbbl').filter(ucbbl=OuterRef('bbl'))
        corerecords = ds.CoreSubsidyRecord.objects.only(
            'bbl').filter(bbl=OuterRef('bbl'))
        publichousingrecords = ds.PublicHousingRecord.objects.only(
            'bbl').filter(bbl=OuterRef('bbl'))
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
        bbls = ds.Property.objects.filter(council=number).only('bbl')
        return self.filter(bbl__in=bbls)

    def community(self, number):
        bbls = ds.Property.objects.filter(cd=number).only('bbl')
        return self.filter(bbl__in=bbls)

    def zipcode(self, number):
        bbls = ds.Property.objects.filter(zipcode=number).only('bbl')
        return self.filter(bbl__in=bbls)

    def stateassembly(self, number):
        bbls = ds.Property.objects.filter(stateassembly=number).only('bbl')
        return self.filter(bbl__in=bbls)

    def statesenate(self, number):
        bbls = ds.Property.objects.filter(statesenate=number).only('bbl')
        return self.filter(bbl__in=bbls)

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
        return queryset

    def council(self, number):
        return self.get_queryset().council(number)

    def community(self, number):
        return self.get_queryset().community(number)

    def council(self, number):
        return self.get_queryset().council(number)

    def zipcode(self, number):
        return self.get_queryset().zipcode(number)

    def stateassembly(self, number):
        return self.get_queryset().stateassembly(number)

    def statesenate(self, number):
        return self.get_queryset().statesenate(number)

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
    SHORT_SUMMARY_FIELDS = ('bbl', 'council', 'cd', 'zipcode', 'yearbuilt', 'unitsres', 'unitstotal',
                            'address', 'latitude', 'longitude', 'stateassembly', 'statesenate')

    # DEPRECATED - now the versin is pulled from the Dataset "Version" field - make sure to include this
    # when creating a Property Update from pluto
    current_version = '20v1'
    objects = PropertyManager()
    current = CurrentPropertyManager()
    obsolete = ObsoletePropertyManager()

    download_endpoint = "https://data.cityofnewyork.us/api/views/64uk-42ks/rows.csv?accessType=DOWNLOAD"
    API_ID = '64uk-42ks'

    # https://www1.nyc.gov/assets/planning/download/pdf/data-maps/open-data/pluto_datadictionary.pdf?r=18v1
    bbl = models.CharField(
        primary_key=True, max_length=10, blank=False, null=False)
    council = models.ForeignKey('Council', on_delete=models.SET_NULL, null=True,
                                db_column='council', db_constraint=False)
    # 1 = manhattan 2 = bronx 3 = brooklyn 4 = queens 5 = staten island
    borough = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)  # 5 digit number
    lot = models.TextField(blank=True, null=True)  # 4 digit number
    cd = models.ForeignKey('Community', on_delete=models.SET_NULL, null=True,
                           db_column='cd', db_constraint=False)
    zipcode = models.ForeignKey('ZipCode', on_delete=models.SET_NULL, null=True,
                                db_column='zipcode', db_constraint=False)
    stateassembly = models.ForeignKey('StateAssembly', on_delete=models.SET_NULL, null=True,
                                      db_column='stateassembly', db_constraint=False)
    statesenate = models.ForeignKey('StateSenate', on_delete=models.SET_NULL, null=True,
                                    db_column='statesenate', db_constraint=False)
    ct2010 = models.TextField(blank=True, null=True)
    cb2010 = models.TextField(blank=True, null=True)
    
    schooldist = models.SmallIntegerField(blank=True, null=True)
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
    bldgclass = models.TextField(blank=True, null=True)
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
    numfloors = models.DecimalField(
        db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    unitsres = models.IntegerField(db_index=True, blank=True, null=True)
    unitstotal = models.IntegerField(db_index=True, blank=True, null=True)
    lotfront = models.DecimalField(
        decimal_places=3, max_digits=32, blank=True, null=True)
    lotdepth = models.DecimalField(
        decimal_places=3, max_digits=32, blank=True, null=True)
    bldgfront = models.DecimalField(
        decimal_places=3, max_digits=32, blank=True, null=True)
    bldgdepth = models.DecimalField(
        decimal_places=3, max_digits=32, blank=True, null=True)
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
    bct2020 = models.TextField(blank=True, null=True)
    bctcb2020 = models.TextField(blank=True, null=True)
    builtfar = models.DecimalField(
        decimal_places=2, max_digits=8, blank=True, null=True)
    residfar = models.DecimalField(
        decimal_places=2, max_digits=8, blank=True, null=True)
    commfar = models.DecimalField(
        decimal_places=2, max_digits=8, blank=True, null=True)
    facilfar = models.DecimalField(
        decimal_places=2, max_digits=8, blank=True, null=True)
    borocode = models.TextField(blank=True, null=True)
    condono = models.TextField(blank=True, null=True)
    tract2010 = models.TextField(blank=True, null=True)
    xcoord = models.IntegerField(blank=True, null=True)
    ycoord = models.IntegerField(blank=True, null=True)
    zonemap = models.TextField(blank=True, null=True)
    zmcode = models.TextField(blank=True, null=True)
    sanborn = models.TextField(blank=True, null=True)
    taxmap = models.TextField(blank=True, null=True)
    edesignum = models.TextField(blank=True, null=True)
    appbbl = models.TextField(blank=True, null=True)
    appdate = models.DateField(blank=True, null=True)
    mapplutof = models.TextField(blank=True, null=True)
    plutomapid = models.TextField(blank=True, null=True)
    firm07flag = models.TextField(blank=True, null=True)
    pfirm15flag = models.TextField(blank=True, null=True)
    rpaddate = models.DateField(blank=True, null=True)
    dcasdate = models.DateField(blank=True, null=True)
    zoningdate = models.DateField(blank=True, null=True)
    landmkdate = models.DateField(blank=True, null=True)
    basempdate = models.DateField(blank=True, null=True)
    masdate = models.DateField(blank=True, null=True)
    polidate = models.DateField(blank=True, null=True)
    edesigdate = models.DateField(blank=True, null=True)
    geom = models.TextField(blank=True, null=True)
    version = models.TextField(db_index=True, blank=True, null=True)
    dcpedited = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=16, decimal_places=14, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=16, decimal_places=14, blank=True, null=True)

    # To conform to socrata
    newnotinold = models.TextField(blank=True, null=True)
    censustract2010 = models.TextField(blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)

    # Custom fields deprecated
    lng = models.DecimalField(
        decimal_places=16, max_digits=32, blank=True, null=True)
    lat = models.DecimalField(
        decimal_places=16, max_digits=32, blank=True, null=True)
    original_address = models.TextField(blank=True, null=True)

    def get_rentstabilized_units(self):
        try:
            return self.rentstabilizationrecord.get_latest_count()
        except Exception as e:
            return 0
    # trims down new update files to preserve memory
    # uses original header values

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def recreate_community_relations(self):
        for property in self.objects.all():
            try:
                property.cd = ds.Community.objects.get(id=property.cd_id)
                property.save()
            except Exception as e:
                logger.debug(
                    'Unable to find community for {}'.format(property))

    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def clean_null_bytes_headers(self, gen_rows):
        gen_rows[0] = gen_rows[0].replace('postcode', 'zipcode')
        gen_rows[0] = gen_rows[0].replace('community board', 'cd')

        for row in gen_rows:
            row = row.replace("\0", "")  # get rid of null-bytes
            row = row.replace("\t", ",")  # switch to csv
            yield row

    @classmethod
    def pre_validation_filters(self, gen_rows):
        logger.info("prevalidating properties")
        count = 0
        for row in gen_rows:
            # Address Standardizing
            row['original_address'] = row['address']
            row['address'] = clean_number_and_streets(
                row['address'], True, clean_typos=False)

            # GEO
            # lng, lat = get_geo(row)
            # row['lat'] = lat
            # row['lng'] = lng
            # Count
            count = count + 1
            if count % 10000 == 0:
                logger.info("prepared {} properties".format(count))

            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update, self.clean_null_bytes_headers))

    # DEPRECATED - KEEP FOR TESTS
    # UPDATE MOCK PLUTO FILES TO versin 20+ which have latitude and longitude included
    @classmethod
    def add_geometry(self):
        logger.info("Attaching geos to properties")
        count = 0
        for record in self.objects.filter(lng__isnull=True, lat__isnull=True).all():
            lng, lat = get_geo(record)
            record.latitude = lat
            record.longitude = lng
            record.save()
            count = count + 1

            if count % 10000 == 0:
                logger.info("attached geos to {} properties".format(count))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.seed_with_upsert(**kwargs)
        logger.info('adding property annotations')
        self.create_property_annotations()
        if settings.TESTING:
            # TODO - update mock pluto datasets to v20+ (mock_pluto_17v1.zip) because newer PLUTO includes latitude and longitude
            self.add_geometry()
        self.add_state_geographies()

    @classmethod
    def add_state_geographies(self):
        logger.info('Adding State Assembly associations via geoshape')
        status1 = self.queryset_foreach(self.objects.filter(stateassembly__isnull=True, latitude__isnull=False, longitude__isnull=False).order_by('pk'), self.create_state_assembly_association, 'stateassembly', batch_size=100)

        logger.info(status1)

        logger.info('Adding State Senate associations via geoshape')
        status2 = self.queryset_foreach(self.objects.filter(statesenate__isnull=True, latitude__isnull=False,
                                                            longitude__isnull=False).order_by('pk'), self.create_state_senate_association, 'statesenate', batch_size=100)
        logger.info(status2)

    @classmethod
    def create_property_annotations(self):
        count = 0
        for property in self.objects.filter(propertyannotation__isnull=True):
            ds.PropertyAnnotation.objects.create(bbl=property)
            if count % 10000 == 0:
                logger.info('property annotations created: {}'.format(count))
            count = count + 1

    @classmethod
    def create_state_assembly_association(self, property, objects_to_update):
        point = Point(property.longitude, property.latitude)
        for stateassembly in ds.StateAssembly.objects.order_by('pk'):
            polygon = shape(stateassembly.data['geometry'])
            if polygon.contains(point):
                property.stateassembly = stateassembly
                objects_to_update.append(property)
                break

        return objects_to_update

    @classmethod
    def create_state_senate_association(self, property, objects_to_update):
        # count = 0
        # for property in self.objects.filter(statesenate__isnull=True, lat__isnull=False, lng__isnull=False):
        point = Point(property.longitude, property.latitude)
        for statesenate in ds.StateSenate.objects.order_by('pk'):
            polygon = shape(statesenate.data['geometry'])
            if polygon.contains(point):
                property.statesenate = statesenate
                objects_to_update.append(property)
                break

        return objects_to_update

    @classmethod
    def queryset_foreach(self, queryset, f, field, batch_size=1000,
                         progress_callback=progress_callback):

        from django.shortcuts import _get_queryset
        queryset = _get_queryset(queryset)
        ids = list(queryset.values_list(
            queryset.model._meta.pk.name, flat=True))
        status = Status()
        status.total = len(ids)

        def do_all_objects(objects, field):
            from django.db import transaction
            with transaction.atomic():
                objects_to_update = []
                for id, obj in objects.items():
                    try:
                        objects_to_update = f(obj, objects_to_update)
                        status.num_successful += 1
                    except Exception as e:
                        logger.error(e)
                        status.failed_ids.append(id)

                self.objects.bulk_update(objects_to_update, [field])

        from django.core.paginator import Paginator
        paginator = Paginator(ids, batch_size)

        status.start()
        progress_callback(status)
        for page_num in paginator.page_range:
            status.page = page = paginator.page(page_num)
            status.cur_idx = page.start_index() - 1
            progress_callback(status)
            objects = queryset.in_bulk(page.object_list)
            do_all_objects(objects, field)
        status.finished()

        progress_callback(status)

        return status

    def __str__(self):
        return str(self.bbl)


@receiver(models.signals.post_save, sender=Property)
def create_property_annotation_on_save(sender, instance, created, **kwargs):
    if created == True:
        annotation = ds.PropertyAnnotation.objects.create(bbl=instance)
        annotation.save()
