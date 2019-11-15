from rest_framework import serializers
from datasets import models as ds
from django.forms.models import model_to_dict
from core.utils.bbl import code_to_boro, abrv_to_borough
from django.conf import settings
from django.db import models
import datetime
import re
from datasets.utils import dates

from datasets.helpers.cache_helpers import is_authenticated
from datasets.helpers.api_helpers import get_annotation_start, get_annotation_end

import logging
logger = logging.getLogger('app')


class CouncilSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Council
        fields = '__all__'


class CouncilSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Council
        fields = '__all__'


class ZipCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.ZipCode
        fields = '__all__'


class StateAssemblySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.StateAssembly
        fields = '__all__'


class StateSenateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.StateSenate
        fields = '__all__'


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Community
        fields = '__all__'


class CouncilSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Community
        fields = '__all__'


class PropertyAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.PropertyAnnotation
        fields = '__all__'

    def to_representation(self, obj):
        rep = super(serializers.ModelSerializer, self).to_representation(obj)
        if not self.context['request'].user.is_authenticated:
            del rep['lispendens_last30']
            del rep['lispendens_lastyear']
            del rep['lispendens_last3years']
            del rep['lispendens_lastupdated']
            del rep['foreclosures_last30']
            del rep['foreclosures_lastyear']
            del rep['foreclosures_last3years']
            del rep['foreclosures_lastupdated']
        return rep


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


class PropertyShortAnnotatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Property
        fields = (ds.Property.SHORT_SUMMARY_FIELDS +
                  ('nycha', 'subsidyprograms', 'subsidyj51', 'subsidy421a', 'unitsrentstabilized', 'latestsaleprice'))

    subsidyprograms = serializers.SerializerMethodField()
    subsidyj51 = serializers.SerializerMethodField()
    subsidy421a = serializers.SerializerMethodField()
    nycha = serializers.SerializerMethodField()
    unitsrentstabilized = serializers.SerializerMethodField()
    latestsaleprice = serializers.SerializerMethodField()

    def get_nycha(self, obj):
        try:
            return obj.propertyannotation.nycha
        except Exception as e:
            return None

    def get_subsidy421a(self, obj):
        try:
            return obj.propertyannotation.subsidy421a
        except Exception as e:
            return None

    def get_subsidyj51(self, obj):
        try:
            return obj.propertyannotation.subsidyj51
        except Exception as e:
            return None

    def get_subsidyprograms(self, obj):
        try:
            return obj.propertyannotation.subsidyprograms
        except Exception as e:
            return None

    def get_unitsrentstabilized(self, obj):
        try:
            return obj.propertyannotation.unitsrentstabilized
        except Exception as e:
            return None

    def get_latestsaleprice(self, obj):
        try:
            return obj.propertyannotation.latestsaleprice
        except Exception as e:
            return None

    def to_representation(self, obj):
        rep = super(serializers.ModelSerializer, self).to_representation(obj)

        params = self.context['request'].query_params

        def get_context_field(dataset_prefix, date_label=None):
            # uses singular dataset_prefix
            for field in self.context['fields']:
                if date_label:
                    if dataset_prefix in field and date_label in field:
                        return field
                else:
                    if dataset_prefix in field:
                        return field
            return None

        for model_name in settings.ANNOTATED_DATASETS:
            dataset_class = getattr(ds, model_name)  # results in query

            if hasattr(dataset_class, 'REQUIRES_AUTHENTICATION') and dataset_class.REQUIRES_AUTHENTICATION and not is_authenticated(self.context['request']):
                continue

            dataset_prefix = dataset_class.__name__.lower()
            if hasattr(obj, dataset_prefix + 's'):
                # annotated from advanced search
                rep[get_context_field(dataset_prefix)] = getattr(obj, dataset_prefix + 's')
            elif 'annotation__start' in params and params['annotation__start'] == 'recent':
                rep[get_context_field(dataset_prefix, 'recent')] = getattr(
                    obj.propertyannotation, dataset_prefix + 's_last30')
            elif 'annotation__start' in params and params['annotation__start'] == 'lastyear':
                rep[get_context_field(dataset_prefix, 'lastyear')] = getattr(
                    obj.propertyannotation, dataset_prefix + 's_lastyear')
            elif 'annotation__start' in params and params['annotation__start'] == 'last3years':
                rep[get_context_field(dataset_prefix, 'last3years')] = getattr(
                    obj.propertyannotation, dataset_prefix + 's_last3years')
            elif 'annotation__start' in params and params['annotation__start'] == 'full':
                rep[get_context_field(dataset_prefix, 'recent')] = getattr(
                    obj.propertyannotation, dataset_prefix + 's_last30')
                rep[get_context_field(dataset_prefix, 'lastyear')] = getattr(
                    obj.propertyannotation, dataset_prefix + 's_lastyear')
                rep[get_context_field(dataset_prefix, 'last3years')] = getattr(
                    obj.propertyannotation, dataset_prefix + 's_last3years')
            elif 'annotation__start' in params:
                if dataset_class == ds.AcrisRealMaster:
                    rep[get_context_field(dataset_prefix)] = getattr(obj, 'acrisreallegal_set').filter(documentid__doctype__in=ds.AcrisRealMaster.SALE_DOC_TYPES).filter(**{'documentid__' + dataset_class.QUERY_DATE_KEY + '__gte': get_annotation_start(
                        params, dataset_class, dataset_class.QUERY_DATE_KEY, dataset_class), 'documentid__' + dataset_class.QUERY_DATE_KEY + '__lte': get_annotation_end(params, dataset_class, dataset_class.QUERY_DATE_KEY, dataset_class)}).count()
                else:
                    rep[get_context_field(dataset_prefix)] = getattr(obj, dataset_prefix + '_set').filter(**{dataset_class.QUERY_DATE_KEY + '__gte': get_annotation_start(
                        params, dataset_class, dataset_class.QUERY_DATE_KEY, dataset_class), dataset_class.QUERY_DATE_KEY + '__lte': get_annotation_end(params, dataset_class, dataset_class.QUERY_DATE_KEY,  dataset_class)}).count()
            else:
                # defaults to recent if no annotation start
                rep[get_context_field(dataset_prefix)] = getattr(
                    obj.propertyannotation, dataset_prefix + 's_last30')
        return rep


class BuildingSummarySerializer(serializers.ModelSerializer):
    # TODO: add alternate addresses derived from AddressRecords' canonical fields
    class Meta:
        model = ds.Building
        fields = (
            'bin', 'stname', 'house_number', 'pad_addresses'
        )
    house_number = serializers.SerializerMethodField()

    def get_house_number(self, obj):
        return obj.get_house_number()


class PropertyShortSummarySerializer(serializers.ModelSerializer):
    subsidyprograms = serializers.SerializerMethodField()
    subsidyj51records = serializers.SerializerMethodField()
    subsidy421arecords = serializers.SerializerMethodField()
    unitsrentstabilized = serializers.SerializerMethodField()

    nycha = serializers.SerializerMethodField()
    rentstabilizationrecord = RentStabilizationIdSerializer(many=False, read_only=True)

    class Meta:
        model = ds.Property
        fields = (ds.Property.SHORT_SUMMARY_FIELDS +
                  ('nycha', 'subsidyprograms', 'rentstabilizationrecord', 'subsidyj51records', 'subsidy421arecords', 'unitsrentstabilized'))

    def get_nycha(self, obj):
        try:
            return obj.propertyannotation.nycha
        except Exception as e:
            return None

    def get_subsidy421a(self, obj):
        try:
            return obj.propertyannotation.subsidy421a
        except Exception as e:
            return None

    def get_subsidyj51(self, obj):
        try:
            return obj.propertyannotation.subsidyj51
        except Exception as e:
            return None

    def get_subsidyprograms(self, obj):
        try:
            return obj.propertyannotation.subsidyprograms
        except Exception as e:
            return None

    def get_unitsrentstabilized(self, obj):
        try:
            return obj.propertyannotation.unitsrentstabilized
        except Exception as e:
            return None


class PropertySummarySerializer(serializers.ModelSerializer):
    hpdregistrations = HPDRegistrationSerializer(source='hpdregistration_set', many=True, read_only=True)
    buildings = BuildingSummarySerializer(source='building_set', many=True, read_only=True)
    rentstabilizationrecord = RentStabilizationRecordSerializer(many=False, read_only=True)
    taxliens = TaxLienSerializer(source='taxlien_set', many=True, read_only=True)
    taxlien = serializers.SerializerMethodField()

    conhrecord = serializers.SerializerMethodField()

    subsidyprograms = serializers.SerializerMethodField()
    subsidyj51 = serializers.SerializerMethodField()
    subsidy421a = serializers.SerializerMethodField()
    nycha = serializers.SerializerMethodField()
    unitsrentstabilized = serializers.SerializerMethodField()

    def get_conhrecord(self, obj):
        try:
            return obj.propertyannotation.conhrecord
        except Exception as e:
            return None

    def get_taxlien(self, obj):
        try:
            return obj.propertyannotation.taxlien
        except Exception as e:
            return None

    def get_nycha(self, obj):
        try:
            return obj.propertyannotation.nycha
        except Exception as e:
            return None

    def get_subsidy421a(self, obj):
        try:
            return obj.propertyannotation.subsidy421a
        except Exception as e:
            return None

    def get_subsidyj51(self, obj):
        try:
            return obj.propertyannotation.subsidyj51
        except Exception as e:
            return None

    def get_subsidyprograms(self, obj):
        try:
            return obj.propertyannotation.subsidyprograms
        except Exception as e:
            return None

    def get_unitsrentstabilized(self, obj):
        try:
            return obj.propertyannotation.unitsrentstabilized
        except Exception as e:
            return None

    class Meta:
        model = ds.Property
        fields = (
            'bbl', 'zipcode', 'council', 'cd', 'borough', 'yearbuilt', 'unitsres', 'unitstotal',
            'bldgclass', 'zonedist1', 'numbldgs', 'numfloors', 'address', 'lat', 'lng', 'ownertype',
            'ownername', 'taxlien', 'taxliens', 'buildings', 'rsunits_percent_lost', 'nycha', 'hpdregistrations',
            'subsidyprograms', 'rentstabilizationrecord', 'unitsrentstabilized', 'subsidyj51', 'subsidy421a', 'conhrecord',
            'zonedist1', 'zonedist2', 'zonedist3', 'zonedist4', 'overlay1', 'overlay2', 'spdist1', 'spdist2', 'spdist3',
            'builtfar', 'residfar', 'commfar', 'facilfar', 'original_address'
        )

    rsunits_percent_lost = serializers.SerializerMethodField()

    def get_rsunits_percent_lost(self, obj):
        try:
            return obj.rentstabilizationrecord.get_percent_lost()
        except Exception as e:
            return 0


class AddressRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.AddressRecord
        fields = '__all__'


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Building
        fields = '__all__'


class PadRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.PadRecord
        fields = '__all__'


#
# class BuildingSearchSerializer(serializers.BaseSerializer):
#     def to_representation(self, obj):
#         return {
#             'bin': obj.bin_id,
#             'bbl': obj.bbl_id,
#             'buildingnumber': obj.buildingnumber,
#             'buildingstreet': obj.buildingstreet,
#             'propertyaddress': obj.propertyaddress,
#             'borough': obj.borough,
#             'zipcode': obj.zipcode,
#             'alternateaddress': obj.alternateaddress
#         }


class BuildingSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.AddressRecord
        fields = '__all__'


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


class DOBFiledPermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBFiledPermit
        fields = '__all__'


class DOBLegacyFiledPermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBLegacyFiledPermit
        fields = '__all__'


class DOBNowFiledPermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.DOBNowFiledPermit
        fields = '__all__'


class LisPendenCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.LisPendenComment
        fields = '__all__'


class LisPendenSerializer(serializers.ModelSerializer):
    comments = LisPendenCommentSerializer(source='lispendencomment_set', many=True, read_only=True)

    class Meta:
        model = ds.LisPenden
        fields = ('key', 'bbl', 'entereddate', 'zip', 'bc', 'fileddate', 'index', 'debtor', 'cr',
                  'attorney', 'thirdparty', 'satdate', 'sattype', 'disp', 'type', 'comments')


class ForeclosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ds.Foreclosure
        fields = ('__all__')


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
