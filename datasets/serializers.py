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


class CouncilHousingTypeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Council
        fields = ('pk', 'housing_types')

    housing_types = serializers.SerializerMethodField()

    def get_housing_types(self, obj):
        council_properties = ds.Property.objects.council(obj.pk)
        program = self.context['request'].query_params['program'] if 'program' in self.context['request'].query_params else None
        unitsres = self.context['request'].query_params['unitsres'] if 'unitsres' in self.context['request'].query_params else '6'

        residential_properties = council_properties.residential()
        rent_stabilized = council_properties.rentstab()
        rent_regulated = council_properties.rentreg(program=program)
        small_homes = council_properties.smallhome(units=unitsres)
        market_rate = council_properties.marketrate()
        public_housing = council_properties.publichousing()

        return {
            "residential_properties": {
                'count': residential_properties.count(),
                'units': residential_properties.aggregate(Sum('unitsres'))['unitsres__sum']
            },
            "rent_stabilized": {
                'count': rent_stabilized.count(),
                'units': rent_stabilized.aggregate(Sum('unitsrentstabilized'))['unitsrentstabilized__sum']
            },
            "rent_regulated": {
                'count': rent_regulated.count(),
                'units': rent_regulated.aggregate(Sum('unitsres'))['unitsres__sum']
            },
            "small_homes":  {
                'count': small_homes.count(),
                'units': small_homes.aggregate(Sum('unitsres'))['unitsres__sum']
            },
            "market_rate": {
                'count': market_rate.count(),
                'units': market_rate.aggregate(Sum('unitsres'))['unitsres__sum']
            },
            "public_housing": {
                'count':  public_housing.count(),
                'units': public_housing.aggregate(Sum('unitsres'))['unitsres__sum']
            }
        }


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Community
        fields = '__all__'


class CouncilSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Community
        fields = '__all__'


class CommunityHousingTypeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Community
        fields = ('pk', 'housing_types')

    housing_types = serializers.SerializerMethodField()

    def get_housing_types(self, obj):
        community_properties = ds.Property.objects.community(obj.pk)
        program = self.context['request'].query_params['program'] if 'program' in self.context['request'].query_params else None
        unitsres = self.context['request'].query_params['unitsres'] if 'unitsres' in self.context['request'].query_params else '6'

        residential_properties = community_properties.residential()
        rent_stabilized = community_properties.rentstab()
        rent_regulated = community_properties.rentreg(program=program)
        small_homes = community_properties.smallhome(units=unitsres)
        market_rate = community_properties.marketrate()
        public_housing = community_properties.publichousing()

        return {
            "residential_properties": {
                'count': residential_properties.count(),
                'units': residential_properties.aggregate(Sum('unitsres'))['unitsres__sum']
            },
            "rent_stabilized": {
                'count': rent_stabilized.count(),
                'units': rent_stabilized.aggregate(Sum('unitsrentstabilized'))['unitsrentstabilized__sum']
            },
            "rent_regulated": {
                'count': rent_regulated.count(),
                'units': rent_regulated.aggregate(Sum('unitsres'))['unitsres__sum']
            },
            "small_homes":  {
                'count': small_homes.count(),
                'units': small_homes.aggregate(Sum('unitsres'))['unitsres__sum']
            },
            "market_rate": {
                'count': market_rate.count(),
                'units': market_rate.aggregate(Sum('unitsres'))['unitsres__sum']
            },
            "public_housing": {
                'count':  public_housing.count(),
                'units': public_housing.aggregate(Sum('unitsres'))['unitsres__sum']
            }
        }


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


class CoreSubsidyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.CoreSubsidyRecord
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Property
        fields = '__all__'


class PropertySummarySerializer(serializers.ModelSerializer):
    hpdregistrations = HPDRegistrationSerializer(source='hpdregistration_set', many=True, read_only=True)
    coresubsidyrecords = CoreSubsidyRecordSerializer(source='coresubsidyrecord_set', many=True, read_only=True)

    class Meta:
        model = ds.Property
        fields = (
            'bbl', 'zipcode', 'council', 'cd', 'borough', 'yearbuilt', 'unitsres', 'unitsrentstabilized', 'unitstotal',
            'bldgclass', 'zonedist1', 'numbldgs', 'numfloors', 'address', 'lat', 'lng', 'ownertype',
            'ownername', 'taxliens', 'buildings', 'nycha', 'hpdregistrations', 'coresubsidyrecords'
        )

    taxliens = serializers.SerializerMethodField()
    buildings = serializers.SerializerMethodField()
    nycha = serializers.SerializerMethodField()

    def get_taxliens(self, obj):
        latest_tax_lien = ds.TaxLien.objects.filter(bbl=obj).order_by('-year').first()

        return latest_tax_lien.year if latest_tax_lien else None

    def get_buildings(self, obj):
        property_buildings = ds.Building.objects.filter(bbl=obj.pk)

        return list({
            "bin": building.bin,
            "house_number": building.get_house_number(),
            "stname": building.stname
        } for building in property_buildings)

    def get_nycha(self, obj):
        return bool(len(ds.PublicHousingRecord.objects.filter(bbl=obj.bbl)))


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

    # def get_problems(self, obj):
    #     import pdb
    #     pdb.set_trace()
    #     try:
    #         return HPDProblemSerializer.serialize(obj.hpd_problem_set)
    #     except Exception as e:
    #         return None


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
