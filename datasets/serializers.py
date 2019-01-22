from rest_framework import serializers
from datasets import models as ds
from django.forms.models import model_to_dict


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
        }


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Property
        fields = '__all__'


class PropertyBuildingsSummary(serializers.ModelSerializer):
    class Meta:
        model = ds.Property
        fields = ('pk', 'buildings')

    buildings = serializers.SerializerMethodField()

    def get_house_number(self, building):
        if (building.lhnd == building.hhnd):
            return building.lhnd
        elif (building.lhnd and building.hhnd):
            return "{}-{}".format(building.lhnd, building.hhnd)
        else:
            return building.lhnd

    def get_buildings(self, obj):
        property_buildings = ds.Building.objects.filter(bbl=obj.pk)

        return {
            "items": list({
                "bin": building.bin,
                "house_number": self.get_house_number(building)
            } for building in property_buildings)
        }


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Building
        fields = '__all__'


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


def property_query_serializer(properties):
    return list({'foo': 'bar'} for property in properties)


def property_lookup_serializer(property):
    property_dict = model_to_dict(property)
    buildings = property.building_set.all()
    hpdcomplaints = property.hpdcomplaint_set.all()
    hpdviolations = property.hpdviolation_set.all()

    def get_house_number(building):
        if (building.lhnd == building.hhnd):
            return building.lhnd
        elif (building.lhnd and building.hhnd):
            return "{}-{}".format(building.lhnd, building.hhnd)
        else:
            return building.lhnd

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
