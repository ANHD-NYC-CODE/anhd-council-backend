from rest_framework import serializers
from datasets import models as ds
from django.forms.models import model_to_dict
from core.utils.bbl import code_to_boro, abrv_to_borough
from django.db.models import Sum


class CouncilSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Council
        fields = '__all__'


class CouncilSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Council
        fields = '__all__'


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Community
        fields = '__all__'


class CouncilSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Community
        fields = '__all__'


class HPDContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDContact
        fields = '__all__'


class HPDRegistrationCsvSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDRegistration
        fields = '__all__'


class HPDRegistrationSerializer(serializers.ModelSerializer):
    contacts = HPDContactSerializer(source='hpdcontact_set', many=True, read_only=True)

    class Meta:
        model = ds.HPDRegistration
        fields = '__all__'


class HPDRegistrationIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDRegistration
        fields = ('pk',)


class CoreSubsidyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.CoreSubsidyRecord
        fields = '__all__'


class CoreSubsidyRecordIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.CoreSubsidyRecord
        fields = ('pk',)


class RentStabilizationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.RentStabilizationRecord
        fields = '__all__'


class RentStabilizationIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.RentStabilizationRecord
        fields = ('pk',)


class PublicHousingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.PublicHousingRecord
        fields = '__all__'


class PublicHousingRecordIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.PublicHousingRecord
        fields = ('pk',)


class SubsidyJ51Serializer(serializers.ModelSerializer):
    class Meta:
        model = ds.SubsidyJ51
        fields = '__all__'


class SubsidyJ51IdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.SubsidyJ51
        fields = ('pk',)


class Subsidy421aSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Subsidy421a
        fields = '__all__'


class Subsidy421aIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Subsidy421a
        fields = ('pk',)


class TaxLienSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.TaxLien
        fields = '__all__'


class TaxLienIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.TaxLien
        fields = ('pk',)


class CONHRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.CONHRecord
        fields = '__all__'


class CONHRecordIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.CONHRecord
        fields = ('pk',)


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Property
        fields = '__all__'


class BuildingSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Building
        fields = (
            'bin', 'stname', 'house_number'
        )
    house_number = serializers.SerializerMethodField()

    def get_house_number(self, obj):
        return obj.get_house_number()


class PropertyShortSummarySerializer(serializers.ModelSerializer):
    subsidyrecords = CoreSubsidyRecordIdSerializer(source='coresubsidyrecord_set', many=True, read_only=True)
    subsidyj51records = SubsidyJ51IdSerializer(source='subsidyj51_set', many=True, read_only=True)
    subsidy421arecords = Subsidy421aIdSerializer(source='subsidy421a_set', many=True, read_only=True)

    nycha = PublicHousingRecordIdSerializer(source='publichousingrecord_set', many=True, read_only=True)
    rentstabilizationrecord = RentStabilizationIdSerializer(many=False, read_only=True)

    class Meta:
        model = ds.Property
        fields = (ds.Property.SHORT_SUMMARY_FIELDS +
                  ('nycha', 'subsidyrecords', 'rentstabilizationrecord', 'subsidyj51records', 'subsidy421arecords'))


class PropertySummarySerializer(serializers.ModelSerializer):
    hpdregistrations = HPDRegistrationSerializer(source='hpdregistration_set', many=True, read_only=True)
    subsidyrecords = CoreSubsidyRecordSerializer(source='coresubsidyrecord_set', many=True, read_only=True)
    subsidyj51records = SubsidyJ51Serializer(source='subsidyj51_set', many=True, read_only=True)
    subsidy421arecords = Subsidy421aSerializer(source='subsidy421a_set', many=True, read_only=True)

    nycha = PublicHousingRecordSerializer(source='publichousingrecord_set', many=True, read_only=True)
    buildings = BuildingSummarySerializer(source='building_set', many=True, read_only=True)
    taxliens = TaxLienSerializer(source='taxlien_set', many=True, read_only=True)
    rentstabilizationrecord = RentStabilizationRecordSerializer(many=False, read_only=True)

    class Meta:
        model = ds.Property
        fields = (
            'bbl', 'zipcode', 'council', 'cd', 'borough', 'yearbuilt', 'unitsres', 'unitsrentstabilized', 'unitstotal',
            'bldgclass', 'zonedist1', 'numbldgs', 'numfloors', 'address', 'lat', 'lng', 'ownertype',
            'ownername', 'taxliens', 'buildings', 'rsunits_percent_lost', 'nycha', 'hpdregistrations', 'subsidyrecords', 'rentstabilizationrecord', 'subsidyj51records', 'subsidy421arecords'
        )

    rsunits_percent_lost = serializers.SerializerMethodField()

    def get_rsunits_percent_lost(self, obj):
        try:
            return obj.rentstabilizationrecord.get_percent_lost()
        except Exception as e:
            return 0


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Building
        fields = '__all__'


class BuildingSearchSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'bin': obj.bin_id,
            'bbl': obj.bbl_id,
            'buildingnumber': obj.buildingnumber,
            'buildingstreet': obj.buildingstreet,
            'propertyaddress': obj.propertyaddress,
            'borough': obj.borough,
            'zipcode': obj.zipcode,
            'alternateaddress': obj.alternateaddress
        }


class HPDBuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDBuildingRecord
        fields = '__all__'


class HPDViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDViolation
        fields = '__all__'


class HPDProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDProblem
        fields = '__all__'


class HPDComplaintCsvSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HPDComplaint
        fields = '__all__'


class HPDComplaintSerializer(serializers.ModelSerializer):
    hpdproblems = HPDProblemSerializer(source='hpdproblem_set', many=True, read_only=True)

    class Meta:
        model = ds.HPDComplaint
        fields = ('complaintid', 'hpdproblems', 'status', 'statusid', 'statusdate', 'apartment', 'receiveddate')


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


class AcrisRealLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.AcrisRealLegal
        fields = '__all__'


class AcrisRealPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.AcrisRealParty
        fields = '__all__'


class AcrisRealMasterCsvSerializer(serializers.ModelSerializer):

    class Meta:
        model = ds.AcrisRealMaster
        fields = '__all__'


class AcrisRealMasterSerializer(serializers.ModelSerializer):
    acrisrealparties = AcrisRealPartySerializer(source='acrisrealparty_set', many=True, read_only=True)

    class Meta:
        model = ds.AcrisRealMaster
        fields = '__all__'


class EvictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Eviction
        fields = '__all__'


class HousingLitigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.HousingLitigation
        fields = '__all__'


class DOBPermitIssuedLegacySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBPermitIssuedLegacy
        fields = '__all__'


class DOBPermitIssuedNowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBPermitIssuedNow
        fields = '__all__'


class DOBIssuedPermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBIssuedPermit
        fields = '__all__'


class DOBLegacyFiledPermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBLegacyFiledPermit
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
            "house_number": building.get_house_number()
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
