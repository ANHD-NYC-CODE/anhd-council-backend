from datasets import models as d_models
from core import models as c_models
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.conf import settings
import os
import zipfile
from datetime import datetime
import random


class BaseTest():
    def clean_tests(self):
        from django_redis import get_redis_connection
        get_redis_connection("default").flushall()
        c_models.DataFile.objects.all().delete()

    def get_file_path(self, name):
        return os.path.join(settings.BASE_DIR, "app/tests/mocks/" + name)

    def update_factory(self, dataset=None, model_name=None, file_name=None, previous_file_name=None):
        if not dataset:
            dataset = c_models.Dataset.objects.create(name=model_name, model_name=model_name)
        file = c_models.DataFile.objects.create(file=self.get_file(file_name), dataset=dataset)

        previous_file = c_models.DataFile.objects.create(file=self.get_file(
            previous_file_name), dataset=dataset) if previous_file_name else None
        update = c_models.Update.objects.create(dataset=dataset, file=file, previous_file=previous_file)
        return update

    def council_factory(self, coundist=None, geometry='{"type":"Polygon","coordinates":[]}', **kwargs):
        name = 'Council'
        if not coundist:
            coundist = random.randint(1, 100000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)

        factory = d_models.Council.objects.create(
            coundist=coundist,
            geometry=geometry,
            **kwargs
        )
        return factory

    def property_factory(self, bbl=None, council=None, unitsres=1, unitstotal=1, borough=1, block='0001', lot='00001', **kwargs):
        name = 'Property'
        if not bbl:
            bbl = random.randint(1000000000, 5999999999)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not council:
            council = self.council_factory(coundist=random.randint(1, 100000))

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
            bin = random.randint(1, 100000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))

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

    def hpdbuilding_factory(self, buildingid=None, property=None, building=None, **kwargs):
        name = 'HPDBuildingRecord'
        if not buildingid:
            buildingid = random.randint(1, 100000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 100000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.HPDBuildingRecord.objects.create(
            buildingid=buildingid,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def hpdcomplaint_factory(self, complaintid=None, property=None, hpdbuilding=None, **kwargs):
        name = 'HPDComplaint'
        if not complaintid:
            complaintid = random.randint(1, 100000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))
        if not hpdbuilding:
            building = self.building_factory(bin=random.randint(1, 100000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)
            hpdbuilding = self.hpdbuilding_factory(buildingid=random.randint(
                1, 100000), property=property, building=building)

        factory = d_models.HPDComplaint.objects.create(
            complaintid=complaintid,
            bbl=property,
            buildingid=hpdbuilding,
            **kwargs
        )
        return factory

    def hpdviolation_factory(self, violationid=None, property=None, building=None, currentstatusid=1, currentstatus="ACTIVE", **kwargs):
        name = 'HPDViolation'
        if not violationid:
            violationid = random.randint(1, 100000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 100000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.HPDViolation.objects.create(
            violationid=violationid,
            bbl=property,
            bin=building,
            currentstatusid=currentstatusid,
            currentstatus=currentstatus,
            **kwargs
        )
        return factory

    def dobcomplaint_factory(self, complaintnumber=None, building=None, **kwargs):
        name = 'DOBComplaint'
        if not complaintnumber:
            complaintnumber = random.randint(1, 100000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not building:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))
            building = self.building_factory(bin=random.randint(1, 100000), property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.DOBComplaint.objects.create(
            complaintnumber=complaintnumber,
            bin=building,
            **kwargs
        )
        return factory

    def dobviolation_factory(self, isndobbisviol=None, property=None, building=None, **kwargs):
        name = 'DOBViolation'
        if not isndobbisviol:
            isndobbisviol = random.randint(1, 100000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 100000), property=property, boro=property.borough,
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
            ecbviolationnumber = random.randint(1, 100000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=random.randint(1, 100000), property=property, boro=property.borough,
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
            documentid = random.randint(1, 100000)
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)

        factory = d_models.AcrisRealMaster.objects.create(
            documentid=documentid,
            **kwargs
        )
        return factory

    def acrisparty_factory(self, master=None, **kwargs):
        name = 'AcrisRealParty'
        if not master:
            master = self.acrismaster_factory(documentid=random.randint(1, 100000))
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)

        factory = d_models.AcrisRealParty.objects.create(
            documentid=master,
            **kwargs
        )
        return factory

    def acrislegal_factory(self, master=None, property=None, **kwargs):
        name = 'AcrisRealLegal'
        if not master:
            master = self.acrismaster_factory(documentid=random.randint(1, 100000))
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))

        factory = d_models.AcrisRealLegal.objects.create(
            documentid=master,
            bbl=property,
            **kwargs
        )
        return factory

    def permitissuedlegacy_factory(self, job=1, permitsino=1, property=None, building=None, **kwargs):
        name = 'DOBPermitIssuedLegacy'
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=1, property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)

        factory = d_models.DOBPermitIssuedLegacy.objects.create(
            job=job,
            permitsino=permitsino,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def permitissuednow_factory(self, jobfilingnumber=1, workpermit=1, issueddate=None, property=None, building=None, **kwargs):
        name = 'DOBPermitIssuedNow'
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))
        if not building:
            building = self.building_factory(bin=1, property=property, boro=property.borough,
                                             block=property.block, lot=property.lot)
        if not issueddate:
            issueddate = datetime.now()
        factory = d_models.DOBPermitIssuedNow.objects.create(
            jobfilingnumber=jobfilingnumber,
            workpermit=workpermit,
            issueddate=issueddate,
            bbl=property,
            bin=building,
            **kwargs
        )
        return factory

    def rentstabilizationrecord_factory(self, property=None, **kwargs):
        name = 'RentStabilizationRecord'
        if not len(c_models.Dataset.objects.filter(name=name)):
            dataset = c_models.Dataset.objects.create(name=name, model_name=name)
        if not property:
            property = self.property_factory(bbl=random.randint(1000000000, 5999999999))

        factory = d_models.RentStabilizationRecord.objects.create(
            ucbbl=property,
            **kwargs
        )
        return factory

    def get_file(self, name):
        file_path = os.path.join(settings.BASE_DIR, "app/tests/mocks/" + name)
        file = File(open(file_path, 'rb'))
        file.name = name
        return file
