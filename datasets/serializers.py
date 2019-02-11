from rest_framework import serializers
from datasets import models as ds
from django.forms.models import model_to_dict
from core.utils.bbl import code_to_boro


def get_house_number(building):
    if (building.lhnd == building.hhnd):
        return building.lhnd
    elif (building.lhnd and building.hhnd):
        return "{}-{}".format(building.lhnd, building.hhnd)
    else:
        return building.lhnd


class CouncilSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Council
        fields = '__all__'


class CouncilHousingTypeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Council
        fields = ('pk', 'housing_types')

    housing_types = serializers.SerializerMethodField()

    def get_housing_types(self, obj):
        council_properties = ds.Property.objects.council(obj.pk)

        return {
            "properties_count": council_properties.count(),
            "rent_stabilized_count": council_properties.rentstab().count(),
            "rent_regulated_count": council_properties.rentreg().count(),
            "small_homes_count": council_properties.smallhome().count(),
            "market_rate_count": council_properties.marketrate().count(),
            "public_housing_count": council_properties.publichousingcount().count()
        }


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Property
        fields = ('bbl', 'council', 'yearbuilt', 'unitsres', 'unitstotal',
                  'bldgclass', 'numbldgs', 'numfloors', 'address', 'lat', 'lng', 'cb2010', 'ct2010')


class PropertySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Property
        fields = (
            'bbl', 'council', 'yearbuilt', 'unitsres', 'unitstotal',
            'bldgclass', 'numbldgs', 'numfloors', 'address', 'lat', 'lng', 'cb2010', 'ct2010',
            'hpdviolations', 'hpdcomplaints', 'dobcomplaints', 'dobviolations', 'ecbviolations',
            'acrisrealmasters', 'hpdregistration', 'hpdregistrationcontacts',
            'coresubsidyrecords', 'dobpermitsissued', 'dobpermitfiled',
            'housinglitigations', 'taxliens', 'evictions', 'taxbill', 'lispendens', 'buildings'
        )

    hpdcomplaints = serializers.SerializerMethodField()

    def get_hpdcomplaints(self, obj):
        hpdcomplaints = ds.HPDComplaint.objects.filter(bbl=obj).all()

        return {
            "count": len(hpdcomplaints)
        }

    hpdviolations = serializers.SerializerMethodField()

    def get_hpdviolations(self, obj):
        hpdviolations = ds.HPDViolation.objects.filter(bbl=obj).all()

        return {
            "count": len(hpdviolations)
        }

    dobcomplaints = serializers.SerializerMethodField()

    def get_dobcomplaints(self, obj):
        dobcomplaints = ds.DOBComplaint.objects.filter(bbl=obj).all()

        return {
            "count": len(dobcomplaints)
        }

    dobviolations = serializers.SerializerMethodField()

    def get_dobviolations(self, obj):
        dobviolations = ds.DOBViolation.objects.filter(bbl=obj).all()

        return {
            "count": len(dobviolations)
        }

    ecbviolations = serializers.SerializerMethodField()

    def get_ecbviolations(self, obj):
        ecbviolations = ds.ECBViolation.objects.filter(bbl=obj).all()

        return {
            "count": len(ecbviolations)
        }

    acrisrealmasters = serializers.SerializerMethodField()

    def get_acrisrealmasters(self, obj):
        acrisrealmasters = ds.AcrisRealMaster.objects.prefetch_related(
            'acrisreallegal_set').filter(acrisreallegal__bbl=obj).all()

        return {
            "count": len(acrisrealmasters)
        }

    hpdregistration = serializers.SerializerMethodField()

    def get_hpdregistration(self, obj):
        hpdregistration = ds.HPDRegistration.objects.filter(bbl=obj).all()

        return {
            "count": len(hpdregistration)
        }

    hpdregistrationcontacts = serializers.SerializerMethodField()

    def get_hpdregistrationcontacts(self, obj):
        hpdregistrationcontacts = ds.HPDContact.objects.filter(registrationid__bbl=obj).all()

        return {
            "count": len(hpdregistrationcontacts)
        }

    coresubsidyrecords = serializers.SerializerMethodField()

    def get_coresubsidyrecords(self, obj):
        coresubsidyrecords = ds.CoreSubsidyRecord.objects.filter(bbl=obj).all()

        return {
            "count": len(coresubsidyrecords)
        }

    dobpermitsissued = serializers.SerializerMethodField()

    def get_dobpermitsissued(self, obj):
        dobpermitsissued = ds.DOBPermitIssuedJoined.objects.filter(bbl=obj).all()

        return {
            "count": len(dobpermitsissued)
        }

    dobpermitfiled = serializers.SerializerMethodField()

    def get_dobpermitfiled(self, obj):
        dobpermitfiled = ds.DOBPermitFiledLegacy.objects.filter(bbl=obj).all()

        return {
            "count": len(dobpermitfiled)
        }

    housinglitigations = serializers.SerializerMethodField()

    def get_housinglitigations(self, obj):
        housinglitigations = ds.HousingLitigation.objects.filter(bbl=obj).all()

        return {
            "count": len(housinglitigations)
        }

    taxliens = serializers.SerializerMethodField()

    def get_taxliens(self, obj):
        taxliens = ds.TaxLien.objects.filter(bbl=obj).all()

        return {
            "count": len(taxliens)
        }

    evictions = serializers.SerializerMethodField()

    def get_evictions(self, obj):
        evictions = ds.Eviction.objects.filter(bbl=obj).all()

        return {
            "count": len(evictions)
        }

    taxbill = serializers.SerializerMethodField()

    def get_taxbill(self, obj):
        taxbill = ds.RentStabilizationRecord.objects.filter(ucbbl=obj).all()

        return {
            "count": len(taxbill)
        }

    lispendens = serializers.SerializerMethodField()

    buildings = serializers.SerializerMethodField()

    def get_buildings(self, obj):
        property_buildings = ds.Building.objects.filter(bbl=obj.pk)

        return {
            "items": list({
                "bin": building.bin,
                "house_number": get_house_number(building)
            } for building in property_buildings)
        }

    def get_lispendens(self, obj):
        return {
            "count": 0,
            "message": "Please sign in to view LisPendens",
            "items": []
        }


class AuthenticatedPropertySummarySerializer(PropertySummarySerializer, serializers.ModelSerializer):

    def get_lispendens(self, obj):
        lispendens = ds.LisPenden.objects.filter(bbl=obj).all()

        return {
            "count": len(lispendens)
        }


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Building
        fields = '__all__'


class BuildingSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.AddressRecord
        fields = ('bin', 'bbl', 'borough', 'number', 'housenumber', 'street', 'zipcode')

    housenumber = serializers.SerializerMethodField()
    # street = serializers.SerializerMethodField()
    # rank = serializers.SerializerMethodField()

    def get_housenumber(self, obj):
        return get_house_number(obj.bin)


class HPDBuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDBuildingRecord
        fields = '__all__'


class HPDViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDViolation
        fields = '__all__'


class HPDComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDComplaint
        fields = '__all__'

    bin = serializers.SerializerMethodField()

    def get_bin(self, obj):
        try:
            return obj.buildingid.bin.bin
        except Exception as e:
            return None


class HPDProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDProblem
        fields = '__all__'


class DOBViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBViolation
        fields = '__all__'


class DOBComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBComplaint
        fields = '__all__'

    bbl = serializers.SerializerMethodField()

    def get_bbl(self, obj):
        try:
            return obj.bin.bbl.bbl
        except Exception as e:
            return None


class ECBViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.ECBViolation
        fields = '__all__'


class AcrisRealMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.AcrisRealMaster
        fields = '__all__'


class AcrisRealLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.AcrisRealLegal
        fields = '__all__'


class AcrisRealPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.AcrisRealParty
        fields = '__all__'


class EvictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Eviction
        fields = '__all__'


class HousingLitigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HousingLitigation
        fields = '__all__'


class HPDRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDRegistration
        fields = '__all__'


class HPDContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDContact
        fields = '__all__'


class TaxLienSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.TaxLien
        fields = '__all__'


class RentStabilizationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.RentStabilizationRecord
        fields = '__all__'


class SubsidyJ51Serializer(serializers.ModelSerializer):
    class Meta:
        model = ds.SubsidyJ51
        fields = '__all__'


class Subsidy421aSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Subsidy421a
        fields = '__all__'


class CoreSubsidyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.CoreSubsidyRecord
        fields = '__all__'


class DOBPermitIssuedLegacySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBPermitIssuedLegacy
        fields = '__all__'


class DOBPermitIssuedNowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBPermitIssuedNow
        fields = '__all__'


class DOBPermitIssuedJoinedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBPermitIssuedJoined
        fields = '__all__'


class DOBPermitFiledLegacySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBPermitFiledLegacy
        fields = '__all__'


class PublicHousingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.PublicHousingRecord
        fields = '__all__'


class LisPendenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.LisPenden
        fields = '__all__'


def property_query_serializer(properties):
    return list({'foo': 'bar'} for property in properties)


def property_lookup_serializer(property):
    property_dict = model_to_dict(property)
    buildings = property.building_set.all()
    hpdcomplaints = property.hpdcomplaint_set.all()
    hpdviolations = property.hpdviolation_set.all()

    property_dict["buildings"] = {
        "total": buildings.count(),
        "items": list({
            "bin": building.bin,
            "house_number": get_house_number(building)
        } for building in buildings)
    }

    property_dict["hpdcomplaints"] = {
        "total": hpdcomplaints.count(),
        "items": [
            model_to_dict(hpdcomplaint) for hpdcomplaint in hpdcomplaints
        ]
    }

    property_dict["hpdviolations"] = {
        "total": hpdviolations.count(),
        "items": [
            model_to_dict(hpdviolation) for hpdviolation in hpdviolations
        ]
    }

    return property_dict
