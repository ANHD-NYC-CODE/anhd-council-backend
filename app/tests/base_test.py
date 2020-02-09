from datasets import models as d_models
from core import models as c_models
from users.models import CustomUser, UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.conf import settings
from rest_framework.test import APITestCase, URLPatternsTestCase
from django.urls import include, path
from rest_framework_simplejwt import views as jwt_views
from django_celery_results.models import TaskResult
import os
import zipfile
from django.utils import timezone
import random
from django.core.cache import cache
import datetime


class BaseTest(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('', include('users.urls')),
        path('', include('datasets.urls')),
        path('', include('core.urls')),
        path('api/token/', jwt_views.TokenObtainPairView.as_view(),
             name='token_obtain_pair'),
        path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(),
             name='token_refresh'),
    ]

    def clean_tests(self):
        # from django_redis import get_redis_connection
        # get_redis_connection("default").flushall()
        # c_models.DataFile.objects.all().delete()
        cache.clear()
        self.clean_mock_files()

    def clean_mock_files(self):
        path = settings.MEDIA_ROOT
        files = [i for i in os.listdir(path)
                 if os.path.isfile(os.path.join(path, i)) and 'mock' in i]
        for file in files:
            os.remove(os.path.join(path, file))

        path = settings.MEDIA_TEMP_ROOT
        files = [i for i in os.listdir(path)
                 if os.path.isfile(os.path.join(path, i)) and 'mock' in i]
        for file in files:
            os.remove(os.path.join(path, file))

    def get_access_token(self, username=None, password=None):
        if not username or not password:
            username = "test"
            password = "test1234!"
            user = self.user_factory(
                email="test@test.com",  username=username, password=password)

        response = self.client.post(
            '/api/token/', {'username': username, 'password': password}, format="json")

        return response.data['access']

    def get_file_path(self, name):
        return os.path.join(settings.BASE_DIR, "app/tests/mocks/" + name)

    def get_file(self, name):
        file_path = os.path.join(settings.BASE_DIR, "app/tests/mocks/" + name)
        file = File(open(file_path, 'rb'))
        file.name = name
        return file

    def create_annotated_datasets(self, start_date=None):
        if not start_date:
            start_date = datetime.datetime.today()
        for dataset_name in settings.ANNOTATED_DATASETS:
            self.dataset_factory(
                name=dataset_name, api_last_updated=start_date)

    def user_factory(self, username=None, password=None, **kwargs):
        if not username:
            username = random.randint(1, 1000000)
        if not password:
            password = random.randint(1, 1000000),

        factory = CustomUser.objects.create_user(
            username=username,
            password=password,
            is_active=True,
            **kwargs
        )
        return factory

    def userprofile_factory(self, user=None, council=None, **kwargs):
        if not user:
            user = self.user_factory()
        if not council:
            council = self.council_factory(),

        factory = UserProfile.objects.create(
            user=user,
            council=council,
            **kwargs
        )
        return factory

    def dataset_factory(self, name=None, **kwargs):
        return c_models.Dataset.objects.create(name=name, model_name=name, **kwargs)

    def datafile_factory(self, dataset=None, **kwargs):
        return c_models.DataFile.objects.create(dataset=dataset, **kwargs)

    def update_factory(self, dataset=None, model_name=None, file_name=None, previous_file_name=None, **kwargs):
        if not dataset:
            dataset = c_models.Dataset.objects.create(
                name=model_name, model_name=model_name)

        file = c_models.DataFile.objects.create(file=self.get_file(
            file_name), dataset=dataset) if file_name else None
        previous_file = c_models.DataFile.objects.create(file=self.get_file(
            previous_file_name), dataset=dataset) if previous_file_name else None
        update = c_models.Update.objects.create(
            dataset=dataset, file=file, previous_file=previous_file, task_result=TaskResult.objects.create(task_id=random.randint(1, 1000000), status="SUCCESS"), **kwargs)
        return update

    def council_factory(self, id=None, **kwargs):
        name = 'Council'
        if not id:
            id = random.randint(1, 1000000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(
                name=name, model_name=name)

        factory = d_models.Council.objects.create(
            id=id,
            **kwargs
        )
        return factory

    def community_factory(self, id=None, **kwargs):
        name = 'Community'
        if not id:
            id = random.randint(1, 1000000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(
                name=name, model_name=name)

        factory = d_models.Community.objects.create(
            id=id,
            **kwargs
        )
        return factory

    def state_assembly_factory(self, id=None, **kwargs):
        name = 'StateAssembly'
        if not id:
            id = random.randint(1, 1000000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(
                name=name, model_name=name)

        factory = d_models.StateAssembly.objects.create(
            id=id,
            **kwargs
        )
        return factory

    def state_senate_factory(self, id=None, **kwargs):
        name = 'StateSenate'
        if not id:
            id = random.randint(1, 1000000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(
                name=name, model_name=name)

        factory = d_models.StateSenate.objects.create(
            id=id,
            **kwargs
        )
        return factory

    def zipcode_factory(self, id=None, **kwargs):
        name = 'ZipCode'
        if not id:
            id = random.randint(1, 1000000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(
                name=name, model_name=name)

        factory = d_models.ZipCode.objects.create(
            id=id,
            **kwargs
        )
        return factory

    def property_factory(self, bbl=None, council=None, unitsres=1, unitstotal=1, borough=1, block='0001', lot='00001', **kwargs):
        name = 'Property'
        if not bbl:
            bbl = random.randint(1000000000, 5999999999)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(
                name=name, model_name=name)
        if not council:
            council = self.council_factory(id=random.randint(1, 1000000))

        factory = d_models.Property.objects.create(
            bbl=bbl,
            council=council,
            unitsres=unitsres,
            unitstotal=unitstotal,
            borough=borough,
            block=block,
            lot=lot,
            **kwargs
        )
        return factory

    def building_factory(self, bin=None, property=None, boro=1, block='0001', lot='00001', lhnd='1a', hhnd='1b', **kwargs):
        name = 'Building'
        if not bin:
            bin = random.randint(1, 1000000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(
                name=name, model_name=name)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.Building.objects.create(
            bin=bin,
            bbl=property,
            boro=boro,
            block=block,
            lot=lot,
            lhnd=lhnd,
            hhnd=hhnd,
            **kwargs
        )
        return factory

    def padrecord_factory(self, bin=None, property=None, building=None, boro=1, block='0001', lot='00001', lhnd='1a', hhnd='1b', **kwargs):
        name = 'PadRecord'
        if not building:
            bin = self.building_factory(
                bin=random.randint(1000000000, 5999999999))
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(
                name=name, model_name=name)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.PadRecord.objects.create(
            key=random.randint(1, 1000000),
            bin=building,
            bbl=property,
            boro=boro,
            block=block,
            lot=lot,
            lhnd=lhnd,
            hhnd=hhnd,
            **kwargs
        )
        return factory

    def address_factory(self, building=None, property=None, **kwargs):
        name = 'AddressRecord'
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.AddressRecord.objects.create(
            key=str(random.randint(1, 1000000)),
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def hpdbuilding_factory(self, buildingid=None, property=None, building=None, **kwargs):
        name = 'HPDBuildingRecord'
        if not buildingid:
            buildingid = random.randint(1, 1000000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(
                name=name, model_name=name)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.HPDBuildingRecord.objects.create(
            buildingid=buildingid,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def hpdcomplaint_factory(self, complaintid=None, property=None, building=None, hpdbuilding=None, **kwargs):
        name = 'HPDComplaint'
        if not complaintid:
            complaintid = random.randint(1, 1000000)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)
        if not hpdbuilding:
            hpdbuilding = self.hpdbuilding_factory(buildingid=random.randint(
                1, 100000), property=property, building=building)

        factory = d_models.HPDComplaint.objects.create(
            complaintid=complaintid,
            bbl=property,
            bin=building,
            buildingid=hpdbuilding,
            **kwargs
        )
        return factory

    def hpdproblem_factory(self, problemid=None, complaint=None, **kwargs):
        name = 'HPDProblem'
        if not problemid:
            problemid = random.randint(1, 1000000)
        if not complaint:
            complaint = self.hpdcomplaint_factory(
                property=property, hpdbuilding=hpdbuilding)

        factory = d_models.HPDProblem.objects.create(
            problemid=problemid,
            complaintid=complaint,
            **kwargs
        )
        return factory

    def propertyannotation_factory(self, property, **kwargs):
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.PropertyAnnotation.objects.create(
            bbl=property
        )

    def hpdviolation_factory(self, violationid=None, property=None, building=None, hpdbuilding=None, currentstatusid=1, currentstatus="ACTIVE", **kwargs):
        name = 'HPDViolation'
        if not violationid:
            violationid = random.randint(1, 1000000)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.HPDViolation.objects.create(
            violationid=violationid,
            bbl=property,
            bin=building,
            buildingid=hpdbuilding,
            currentstatusid=currentstatusid,
            currentstatus=currentstatus,
            **kwargs
        )
        return factory

    def hpdregistration_factory(self, registrationid=None, property=None, building=None, hpdbuilding=None, **kwargs):
        name = 'HPDRegistration'
        if not registrationid:
            registrationid = random.randint(1, 1000000)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.HPDRegistration.objects.create(
            registrationid=registrationid,
            bbl=property,
            bin=building,
            buildingid=hpdbuilding,
            **kwargs
        )
        return factory

    def hpdcontact_factory(self, registrationcontactid=None, registration=None, **kwargs):
        name = 'HPDContact'

        if not registrationcontactid:
            registrationcontactid = random.randint(1, 1000000)

        if not registration:
            registration = self.hpdregistration_factory(
                registrationid=random.randint(1, 1000000))

        factory = d_models.HPDContact.objects.create(
            registrationcontactid=registrationcontactid,
            registrationid=registration,
            **kwargs
        )
        return factory

    def dobcomplaint_factory(self, complaintnumber=None, building=None, property=None, **kwargs):
        name = 'DOBComplaint'
        if not complaintnumber:
            complaintnumber = random.randint(1, 1000000)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.DOBComplaint.objects.create(
            complaintnumber=complaintnumber,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def dobviolation_factory(self, isndobbisviol=None, property=None, building=None, **kwargs):
        name = 'DOBViolation'
        if not isndobbisviol:
            isndobbisviol = random.randint(1, 1000000)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.DOBViolation.objects.create(
            isndobbisviol=isndobbisviol,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def ecbviolation_factory(self, ecbviolationnumber=None, property=None, building=None, **kwargs):
        name = 'ECBViolation'
        if not ecbviolationnumber:
            ecbviolationnumber = random.randint(1, 1000000)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.ECBViolation.objects.create(
            ecbviolationnumber=ecbviolationnumber,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def acrismaster_factory(self, documentid=None, **kwargs):
        name = 'AcrisRealMaster'
        if not documentid:
            documentid = random.randint(1, 1000000)

        factory = d_models.AcrisRealMaster.objects.create(
            documentid=documentid,
            **kwargs
        )
        return factory

    def acrisparty_factory(self, master=None, **kwargs):
        name = 'AcrisRealParty'
        if not master:
            master = self.acrismaster_factory(
                documentid=random.randint(1, 1000000))

        factory = d_models.AcrisRealParty.objects.create(
            key=random.randint(1000000000, 5999999999),
            documentid=master,
            **kwargs
        )
        return factory

    def acrislegal_factory(self, master=None, property=None, **kwargs):
        name = 'AcrisRealLegal'
        if not master:
            master = self.acrismaster_factory(
                documentid=random.randint(1, 1000000))

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.AcrisRealLegal.objects.create(
            key=random.randint(1000000000, 5999999999),
            documentid=master,
            bbl=property,
            **kwargs
        )
        return factory

    def doblegacyfiledpermit_factory(self, job=None, jobs1no=None, property=None, building=None, **kwargs):
        name = 'DOBLegacyFiledPermit'
        if not job:
            job = random.randint(1, 1000000)
        if not jobs1no:
            jobs1no = random.randint(1, 1000000)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.DOBLegacyFiledPermit.objects.create(
            job=job,
            jobs1no=jobs1no,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def dobnowfiledpermit_factory(self, jobfilingnumber=None, property=None, **kwargs):
        name = 'DOBNowFiledPermit'
        if not jobfilingnumber:
            jobfilingnumber = random.randint(1, 1000000)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.DOBNowFiledPermit.objects.create(
            jobfilingnumber=jobfilingnumber,
            bbl=property,
            **kwargs
        )
        return factory

    def permitissuednow_factory(self, jobfilingnumber=None, workpermit=None, issueddate=None, property=None, building=None, **kwargs):
        name = 'DOBPermitIssuedNow'

        if not workpermit:
            workpermit = random.randint(1, 1000000)
        if not jobfilingnumber:
            jobfilingnumber = random.randint(1, 1000000)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)
        if not issueddate:
            issueddate = timezone.now()
        factory = d_models.DOBPermitIssuedNow.objects.create(
            jobfilingnumber=jobfilingnumber,
            workpermit=workpermit,
            issueddate=issueddate,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def dobissuedpermit_factory(self, jobfilingnumber=None, workpermit=None, property=None, building=None, **kwargs):
        name = 'DOBIssuedPermit'

        if not workpermit:
            workpermit = random.randint(1, 1000000)
        if not jobfilingnumber:
            jobfilingnumber = random.randint(1, 1000000)

        key = "{}{}".format(workpermit, jobfilingnumber)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)
        factory = d_models.DOBIssuedPermit.objects.create(
            key=key,
            jobfilingnumber=jobfilingnumber,
            workpermit=workpermit,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def dobfiledpermit_factory(self, jobfilingnumber=None, property=None, building=None, **kwargs):
        name = 'DOBIssuedPermit'

        if not jobfilingnumber:
            jobfilingnumber = random.randint(1, 1000000)

        key = "{}{}".format(random.randint(1, 1000000), jobfilingnumber)

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)
        factory = d_models.DOBFiledPermit.objects.create(
            key=key,
            jobfilingnumber=jobfilingnumber,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def permitissuedlegacy_factory(self, job=None, permitsino=None, property=None, building=None, **kwargs):
        name = 'DOBPermitIssuedLegacy'
        if not job:
            job = random.randint(1, 1000000)
        if not permitsino:
            permitsino = random.randint(1, 1000000)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.DOBPermitIssuedLegacy.objects.create(
            job=job,
            permitsino=permitsino,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def taxbill_factory(self, property=None, **kwargs):
        name = 'RentStabilizationRecord'
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.RentStabilizationRecord.objects.create(
            ucbbl=property,
            **kwargs
        )
        return factory

    def eviction_factory(self, id=None, property=None, **kwargs):
        name = 'Eviction'
        if not id:
            id = random.randint(1, 1000000)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.Eviction.objects.create(
            courtindexnumber=id,
            bbl=property,
            **kwargs
        )
        return factory

    def housinglitigation_factory(self, litigationid=None, property=None, building=None, **kwargs):
        name = 'HousingLitigation'
        if not litigationid:
            litigationid = random.randint(1, 1000000)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 1000000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.HousingLitigation.objects.create(
            litigationid=litigationid,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def taxlien_factory(self, property=None, **kwargs):
        name = 'TaxLien'

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.TaxLien.objects.create(
            bbl=property,
            **kwargs
        )
        return factory

    def conhrecord_factory(self, property=None, **kwargs):
        name = 'CONHRecord'

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.CONHRecord.objects.create(
            bbl=property,
            **kwargs
        )
        return factory

    def subsidyj51_factory(self, property=None, **kwargs):
        name = 'SubsidyJ51'

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.SubsidyJ51.objects.create(
            bbl=property,
            **kwargs
        )
        return factory

    def subsidy421a_factory(self, property=None, **kwargs):
        name = 'Subsidy421a'

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.Subsidy421a.objects.create(
            bbl=property,
            **kwargs
        )
        return factory

    def coredata_factory(self, property=None, **kwargs):
        name = 'CoreData'

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.CoreSubsidyRecord.objects.create(
            bbl=property,
            **kwargs
        )
        return factory

    def publichousingrecord_factory(self, property=None, **kwargs):
        name = 'PublicHousingRecord'

        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.PublicHousingRecord.objects.create(
            bbl=property,
            **kwargs
        )
        return factory

    def lispenden_factory(self, key=None, property=None, **kwargs):
        name = 'LisPenden'
        if not key:
            key = random.randint(1, 1000000)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.LisPenden.objects.create(
            key=key,
            bbl=property,
            **kwargs
        )
        return factory

    def foreclosure_factory(self, key=None, property=None, **kwargs):
        name = 'Foreclosure'
        if not key:
            key = random.randint(1, 1000000)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.Foreclosure.objects.create(
            key=key,
            bbl=property,
            **kwargs
        )
        return factory

    def foreclosure_auction_factory(self, key=None, property=None, **kwargs):
        name = 'PSForeclosure'
        if not key:
            key = random.randint(1, 1000000)
        if not property:
            property = self.property_factory(
                bbl=random.randint(1000000000, 5999999999))

        factory = d_models.PSForeclosure.objects.create(
            key=key,
            bbl=property,
            **kwargs
        )
        return factory
