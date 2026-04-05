from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than, does_not_contain_values
import logging
from core.tasks import async_download_and_update


logger = logging.getLogger('app')

# Update process: Automatic
# Update strategy: Overwrite
#


class DOBPermitIssuedLegacy(BaseDatasetModel, models.Model):
    API_ID = 'ipu4-2q9a'
    download_endpoint = "https://data.cityofnewyork.us/api/views/ipu4-2q9a/rows.csv?accessType=DOWNLOAD"
    base_download_endpoint = "https://data.cityofnewyork.us/resource/ipu4-2q9a.csv"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['bbl', 'bin', 'job', 'permitsino'], name='uuid')
        ]

    job = models.TextField(blank=False, null=False)
    permitsino = models.TextField(blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    house = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    jobdoc = models.TextField(blank=True, null=True)
    jobtype = models.TextField(blank=True, null=True)
    selfcert = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    communityboard = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    bldgtype = models.TextField(blank=True, null=True)
    residential = models.TextField(blank=True, null=True)
    specialdistrict1 = models.TextField(blank=True, null=True)
    specialdistrict2 = models.TextField(blank=True, null=True)
    worktype = models.TextField(blank=True, null=True)
    permitstatus = models.TextField(blank=True, null=True)
    filingstatus = models.TextField(blank=True, null=True)
    permittype = models.TextField(blank=True, null=True)
    permitsequence = models.TextField(blank=True, null=True)
    permitsubtype = models.TextField(blank=True, null=True)
    oilgas = models.TextField(blank=True, null=True)
    sitefill = models.TextField(blank=True, null=True)
    filingdate = models.DateField(blank=True, null=True)
    issuancedate = models.DateField(blank=True, null=True)
    expirationdate = models.DateField(blank=True, null=True)
    jobstartdate = models.DateField(blank=True, null=True)
    permitteesfirstname = models.TextField(blank=True, null=True)
    permitteeslastname = models.TextField(blank=True, null=True)
    permitteesbusinessname = models.TextField(blank=True, null=True)
    permitteesphone = models.TextField(blank=True, null=True)
    permitteeslicensetype = models.TextField(blank=True, null=True)
    permitteeslicense = models.TextField(blank=True, null=True)
    actassuperintendent = models.TextField(blank=True, null=True)
    permitteesothertitle = models.TextField(blank=True, null=True)
    hiclicense = models.TextField(blank=True, null=True)
    sitesafetymgrsfirstname = models.TextField(blank=True, null=True)
    sitesafetymgrslastname = models.TextField(blank=True, null=True)
    sitesafetymgrbusinessname = models.TextField(blank=True, null=True)
    superintendentfirstlastname = models.TextField(blank=True, null=True)
    superintendentbusinessname = models.TextField(blank=True, null=True)
    ownersbusinesstype = models.TextField(blank=True, null=True)
    nonprofit = models.TextField(blank=True, null=True)
    ownersbusinessname = models.TextField(blank=True, null=True)
    ownersfirstname = models.TextField(blank=True, null=True)
    ownerslastname = models.TextField(blank=True, null=True)
    ownershouse = models.TextField(blank=True, null=True)
    ownershousestreetname = models.TextField(blank=True, null=True)
    ownershousecity = models.TextField(blank=True, null=True)
    ownershousestate = models.TextField(blank=True, null=True)
    ownershousezipcode = models.TextField(blank=True, null=True)
    ownersphone = models.TextField(blank=True, null=True)
    dobrundate = models.DateField(blank=True, null=True)
    latitude = models.DecimalField(
        decimal_places=8, max_digits=16, blank=True, null=True)
    longitude = models.DecimalField(
        decimal_places=8, max_digits=16, blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    ntaname = models.TextField(blank=True, null=True)

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        fields = [
            "job__", "permit_si_no", "borough", "bin__", "house__", "street_name",
            "block", "lot", "work_type", "job_type", "permit_status", "filing_status",
            "permit_type", "permit_subtype",
            "issuance_date", "expiration_date",
            "permittee_s_first_name", "permittee_s_last_name", "permittee_s_business_name",
            "owner_s_first_name", "owner_s_last_name", "owner_s_business_name",
            "dobrundate"
        ]
        download_url = "{}?$select={}&$limit=100000000".format(
            self.base_download_endpoint, ','.join(fields))
        logger.info("Downloading DOBPermitIssuedLegacy filtered dataset from: %s", download_url)
        return self.download_file(download_url, file_name=file_name or "DOBPermitIssuedLegacy")

    # Socrata resource API returns different column names than the CSV export
    SOCRATA_FIELD_MAP = {
        'job__': 'job',
        'permit_si_no': 'permitsino',
        'bin__': 'bin',
        'house__': 'house',
        'street_name': 'streetname',
        'work_type': 'worktype',
        'job_type': 'jobtype',
        'permit_status': 'permitstatus',
        'filing_status': 'filingstatus',
        'permit_type': 'permittype',
        'permit_subtype': 'permitsubtype',
        'issuance_date': 'issuancedate',
        'expiration_date': 'expirationdate',
        'permittee_s_first_name': 'permitteesfirstname',
        'permittee_s_last_name': 'permitteeslastname',
        'permittee_s_business_name': 'permitteesbusinessname',
        'owner_s_first_name': 'ownersfirstname',
        'owner_s_last_name': 'ownerslastname',
        'owner_s_business_name': 'ownersbusinessname',
    }

    @classmethod
    def remap_headers(cls, gen_rows):
        for row in gen_rows:
            remapped = {}
            for key, value in row.items():
                clean_key = key.lstrip('\ufeff')
                new_key = cls.SOCRATA_FIELD_MAP.get(clean_key, clean_key)
                remapped[new_key] = value
            yield remapped

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['job']) or is_null(row['permitsino']):
                continue
            if is_null(row['issuancedate']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if headers.index('Issuance Date') and is_older_than(row[headers.index('Issuance Date')], 2):
                continue
            if does_not_contain_values(["a1", "a2", "dm", "nb"], row[headers.index('Job Type')]):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(self.remap_headers(from_csv_file_to_gen(file_path, update))))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE datasets_dobpermitissuedlegacy RESTART IDENTITY')
        self.seed_with_upsert(**kwargs, overwrite=True)
    def __str__(self):
        return str(self.job)
