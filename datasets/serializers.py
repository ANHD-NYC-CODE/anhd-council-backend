from rest_framework import serializers
from datasets import models as ds
from django.forms.models import model_to_dict


class CouncilSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Council
        fields = '__all__'


class CouncilDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Council
        fields = '__all__'

    housing_types = serializers.SerializerMethodField()

    def get_housing_types(self, obj):
        council_buildings = ds.Property.objects.council(obj.pk)

        return {
            "buildings_count": council_buildings.count(),
            "rent_stabilized_count": council_buildings.rentstab().count(),
            "rent_regulated_count": council_buildings.rentreg().count(),
            "small_homes_count": council_buildings.smallhome().count(),
            "market_rate_count": council_buildings.marketrate().count(),
        }


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Property
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
