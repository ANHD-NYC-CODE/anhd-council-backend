from django.db import models
from django.db.models import Q
from datasets.models.Base import Base as BaseDataset
from core.utils.transform import to_csv, extract_csvs_from_zip, with_geo, remove_non_residential


class CurrentBuildingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(version=self.model.current_version)


class ObsoleteBuildingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(~Q(version=self.model.current_version))


class Building(BaseDataset, models.Model):
    current_version = '18V1'
    objects = models.Manager()
    current = CurrentBuildingManager()
    obsolete = ObsoleteBuildingManager()

    # 763178 +- records for residential buildings.
    # Current version: Pluto18v1
    # To update to latest Pluto version,
    # Compare the columns between the next Pluto version and this.
    # Add, but do not delete any columns if different.
    # Create a django migration to add new columns.
    # Create an Update with the latest pluto zip file in admin panel.
    # Existing buildings will be overritten with latest values.
    # New buildings will be added.
    # Old buildings will not be removed automatically, need manual removal.
    # Building.obsolete.all().delete()
    bbl = models.CharField(primary_key=True, max_length=10, blank=False, null=False)
    council = models.ForeignKey('Council', on_delete=models.SET_NULL, null=True,
                                db_column='council', db_constraint=False)
    borough = models.TextField(blank=False, null=False)
    block = models.TextField(blank=False, null=False)
    lot = models.TextField(blank=False, null=False)
    cd = models.SmallIntegerField(blank=True, null=True)
    ct2010 = models.TextField(blank=True, null=True)
    cb2010 = models.TextField(blank=True, null=True)
    schooldist = models.SmallIntegerField(blank=True, null=True)
    zipcode = models.CharField(max_length=5, blank=True, null=True)
    firecomp = models.TextField(blank=True, null=True)
    policeprct = models.TextField(blank=True, null=True)
    healthcenterdistrict = models.SmallIntegerField(blank=True, null=True)
    healtharea = models.TextField(blank=True, null=True)
    sanitboro = models.CharField(max_length=1, blank=True, null=True)
    sanitdistrict = models.SmallIntegerField(blank=True, null=True)
    sanitsub = models.CharField(max_length=2, blank=True, null=True)
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
    bldgclass = models.CharField(db_index=True, max_length=2, blank=False, null=False)
    landuse = models.SmallIntegerField(blank=True, null=True)
    easements = models.TextField(blank=True, null=True)
    ownertype = models.CharField(max_length=1, blank=True, null=True)
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
    unitsres = models.IntegerField(db_index=True, blank=False, null=False)
    unitstotal = models.IntegerField(db_index=True, blank=False, null=False)
    lotfront = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    lotdepth = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    bldgfront = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    bldgdepth = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    ext = models.TextField(blank=True, null=True)
    proxcode = models.CharField(max_length=1, blank=True, null=True)
    irrlotcode = models.BooleanField(blank=True, null=True)
    lottype = models.CharField(max_length=1, blank=True, null=True)
    bsmtcode = models.CharField(max_length=1, blank=True, null=True)
    assessland = models.BigIntegerField(blank=True, null=True)
    assesstot = models.BigIntegerField(blank=True, null=True)
    exemptland = models.BigIntegerField(blank=True, null=True)
    exempttot = models.BigIntegerField(blank=True, null=True)
    yearbuilt = models.SmallIntegerField(db_index=True, blank=False, null=False)
    yearalter1 = models.SmallIntegerField(blank=True, null=True)
    yearalter2 = models.SmallIntegerField(blank=True, null=True)
    histdist = models.TextField(blank=True, null=True)
    landmark = models.TextField(blank=True, null=True)
    builtfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    residfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    commfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    facilfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    borocode = models.CharField(db_index=True, max_length=1, blank=False, null=False)
    condono = models.TextField(blank=True, null=True)
    tract2010 = models.TextField(blank=True, null=True)
    xcoord = models.IntegerField(blank=True, null=True)
    ycoord = models.IntegerField(blank=True, null=True)
    zonemap = models.TextField(blank=True, null=True)
    zmcode = models.CharField(max_length=1, blank=True, null=True)
    sanborn = models.TextField(blank=True, null=True)
    taxmap = models.TextField(blank=True, null=True)
    edesignum = models.TextField(blank=True, null=True)
    appbbl = models.CharField(db_index=True, max_length=10, blank=True, null=True)
    appdate = models.DateTimeField(blank=True, null=True)
    plutomapid = models.CharField(max_length=1, blank=True, null=True)
    firm07flag = models.CharField(max_length=1, blank=True, null=True)
    pfirm15flag = models.CharField(max_length=1, blank=True, null=True)
    version = models.TextField(db_index=True, blank=True, null=True)
    # allow null lng / lat - will display building information in tables, not map
    lng = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    lat = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)

    @classmethod
    def transform_self(self, file_path):
        return with_geo(remove_non_residential(to_csv(extract_csvs_from_zip(file_path))))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.seed_with_overwrite(**kwargs)

    def __str__(self):
        return self.bbl
