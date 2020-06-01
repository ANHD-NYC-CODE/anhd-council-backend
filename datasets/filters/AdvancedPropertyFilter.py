from datasets import models as ds
import rest_framework_filters as filters
import django_filters
from django.db.models import Count, Q, ExpressionWrapper, F, FloatField, Case, When, Value
from datasets.utils import advanced_filter as af

from datasets.filter_helpers import PercentWithDateField, AdvancedQueryFilter, CommaSeparatedConditionField
from django.db.models import Q

from datasets.filters.PropertyFilter import housingtype_filter, rsunits_filter, programnames_filter
import logging

logger = logging.getLogger('app')


class AdvancedPropertyFilter(django_filters.rest_framework.FilterSet):
    def __init__(self, *args, **kwargs):
        return super(AdvancedPropertyFilter, self).__init__(*args, **kwargs)

    @property
    def qs(self):
        return super(AdvancedPropertyFilter, self).qs

    q = AdvancedQueryFilter(method='filter_advancedquery')

    def filter_advancedquery(self, queryset, name, values):
        # Turns out the queryset that comes here is not guaranteed to be pre-filled with
        # council or housing type filters / subqueries

        # Need to override the queryset to ensure subqueries come before joins
        bbl_queryset = ds.Property.objects
        params = dict(self.request.query_params)

        # converts the param values into an array for some reason...
        del params['q']
        params.pop('summary', None)
        params.pop('summary-type', None)
        if 'format' in params:
            del params['format']
        if 'council' in params:
            bbl_queryset = bbl_queryset.filter(
                bbl__in=bbl_queryset.council(params['council'][0]).values('bbl'))
            del params['council']
        elif 'community' in params:
            bbl_queryset = bbl_queryset.filter(
                bbl__in=bbl_queryset.community(params['community'][0]).values('bbl'))
            del params['community']
        elif 'stateassembly' in params:
            bbl_queryset = bbl_queryset.filter(bbl__in=bbl_queryset.stateassembly(
                params['stateassembly'][0]).values('bbl'))
            del params['stateassembly']
        elif 'statesenate' in params:
            bbl_queryset = bbl_queryset.filter(
                bbl__in=bbl_queryset.statesenate(params['statesenate'][0]).values('bbl'))
            del params['statesenate']
        elif 'zipcode' in params:
            bbl_queryset = bbl_queryset.filter(
                bbl__in=bbl_queryset.zipcode(params['zipcode'][0]).values('bbl'))
            del params['zipcode']
        if 'housingtype' in params:
            bbl_queryset = bbl_queryset.filter(bbl__in=housingtype_filter(
                self, bbl_queryset, name, params['housingtype'][0]).values('bbl'))
            del params['housingtype']
        if 'rsunitslost__start' in params:
            start = params['rsunitslost__start'][0]
            del params['rsunitslost__start']
            end = None
            lt = None
            lte = None
            exact = None
            gt = None
            gte = None
            if 'rsunitslost__end' in params:
                end = params['rsunitslost__end'][0]
                del params['rsunitslost__end']
            if 'rsunitslost__lt' in params:
                lt = params['rsunitslost__lt'][0]
                del params['rsunitslost__lt']
            if 'rsunitslost__lte' in params:
                lte = params['rsunitslost__lte'][0]
                del params['rsunitslost__lte']
            if 'rsunitslost__exact' in params:
                exact = params['rsunitslost__exact'][0]
                del params['rsunitslost__exact']
            if 'rsunitslost__gt' in params:
                gt = params['rsunitslost__gt'][0]
                del params['rsunitslost__gt']
            if 'rsunitslost__gte' in params:
                gte = params['rsunitslost__gte'][0]
                del params['rsunitslost__gte']

            rsunitslost_params = (start,
                                  end,
                                  lt,
                                  lte,
                                  exact,
                                  gt,
                                  gte,)

            bbl_queryset = bbl_queryset.filter(bbl__in=rsunits_filter(self,
                                                                      bbl_queryset, name, PercentWithDateField.compress(self, rsunitslost_params)))

        if 'subsidyprograms__programname' in ''.join(params.keys()):
            if 'subsidyprograms__programname__any' in params:
                programname_params = (
                    params['subsidyprograms__programname__any'][0], None, None, None)
            elif 'subsidyprograms__programname__all' in params:
                programname_params = (
                    None, params['subsidyprograms__programname__all'][0], None, None)
            elif 'subsidyprograms__programname__icontains' in params:
                programname_params = (
                    None, None, None, params['subsidyprograms__programname__icontains'][0])
            else:
                programname_params = (
                    None, None, params['subsidyprograms__programname'][0], None)
            bbl_queryset = bbl_queryset.filter(bbl__in=programnames_filter(
                self, bbl_queryset, 'propertyannotation__subsidyprograms', CommaSeparatedConditionField.compress(self, programname_params)))
        # add all the other params
        for key, value in params.items():
            try:
                bbl_queryset = bbl_queryset.filter(**{key: value[0]})
            except Exception as e:
                print("AdvancedFilter processed a non-property field: {}".format(e))
                logger.debug(
                    "AdvancedFilter processed a non-property field: {}".format(e))

        # finally, construct subquery

        bbl_queryset = bbl_queryset.filter(bbl__in=queryset.only('bbl'))
        # NOW parse the q advanced query
        mapping = af.convert_query_string_to_mapping(values)

        af.validate_mapping(self.request, mapping)

        for con in mapping.keys():
            for c_filter in mapping[con]['filters']:
                if 'condition' in c_filter:
                    # skip condition filters
                    continue

                if c_filter['model'] == 'rentstabilizationrecord':
                    queryset = af.annotate_rentstabilized(queryset, c_filter)
                elif c_filter['model'].lower() == 'acrisreallegal':
                    queryset = af.annotate_acrislegals(
                        queryset, c_filter, bbl_queryset.values('bbl'))

                else:
                    queryset = af.annotate_dataset(
                        queryset, c_filter, bbl_queryset.values('bbl'))

        # q1 = af.convert_condition_to_q(next(iter(mapping)), mapping, 'query1_filters')
        # q1_queryset = queryset.filter(q1)

        # filter on annotating filters (like counts)

        # q1 = af.convert_condition_to_q(next(iter(mapping)), mapping, 'query1_filters')

        q2 = af.convert_condition_to_q(
            next(iter(mapping)), mapping, 'query2_filters')

        queryset = queryset.filter(q2, bbl__in=bbl_queryset.values('bbl'))
        # q2_queryset = q1_queryset.filter(q2)
        #
        # final_bbls = q2_queryset.values('bbl')

        queryset = queryset.defer("ct2010",
                                  "cb2010",
                                  "schooldist",
                                  "firecomp",
                                  "policeprct",
                                  "healthcenterdistrict",
                                  "healtharea",
                                  "sanitboro",
                                  "sanitdistrict",
                                  "sanitsub",
                                  "ltdheight",
                                  "splitzone",
                                  "landuse",
                                  "easements",
                                  "lotarea",
                                  "bldgarea",
                                  "comarea",
                                  "resarea",
                                  "officearea",
                                  "retailarea",
                                  "garagearea",
                                  "strgearea",
                                  "factryarea",
                                  "otherarea",
                                  "areasource",
                                  "lotfront",
                                  "lotdepth",
                                  "bldgfront",
                                  "bldgdepth",
                                  "ext",
                                  "proxcode",
                                  "irrlotcode",
                                  "lottype",
                                  "bsmtcode",
                                  "assessland",
                                  "assesstot",
                                  "exemptland",
                                  "exempttot",
                                  "yearalter1",
                                  "yearalter2",
                                  "histdist",
                                  "landmark",
                                  "builtfar",
                                  "residfar",
                                  "commfar",
                                  "facilfar",
                                  "condono",
                                  "tract2010",
                                  "zonemap",
                                  "zmcode",
                                  "sanborn",
                                  "taxmap",
                                  "edesignum",
                                  "appbbl",
                                  "appdate",
                                  "mapplutof",
                                  "plutomapid",
                                  "firm07flag",
                                  "pfirm15flag",
                                  "rpaddate",
                                  "dcasdate",
                                  "zoningdate",
                                  "landmkdate",
                                  "basempdate",
                                  "masdate",
                                  "polidate",
                                  "edesigdate",
                                  "geom",
                                  "zonedist1",
                                  "zonedist2",
                                  "zonedist3",
                                  "zonedist4",
                                  "overlay1",
                                  "overlay2",
                                  "spdist1",
                                  "spdist2",
                                  "spdist3",
                                  "ownertype",
                                  "ownername",
                                  "numbldgs",
                                  "numfloors",
                                  "xcoord",
                                  "ycoord",
                                  "version",
                                  "borocode",
                                  "bldgclass",
                                  "original_address",
                                  "dcpedited",
                                  "notes",
                                  "latitude",
                                  "longitude").defer(
            "propertyannotation__hpdviolations_last30",
            "propertyannotation__hpdviolations_lastyear",
            "propertyannotation__hpdviolations_last3years",
            "propertyannotation__hpdviolations_lastupdated",
            "propertyannotation__hpdcomplaints_last30",
            "propertyannotation__hpdcomplaints_lastyear",
            "propertyannotation__hpdcomplaints_last3years",
            "propertyannotation__hpdcomplaints_lastupdated",
            "propertyannotation__dobviolations_last30",
            "propertyannotation__dobviolations_lastyear",
            "propertyannotation__dobviolations_last3years",
            "propertyannotation__dobviolations_lastupdated",
            "propertyannotation__dobcomplaints_last30",
            "propertyannotation__dobcomplaints_lastyear",
            "propertyannotation__dobcomplaints_last3years",
            "propertyannotation__dobcomplaints_lastupdated",
            "propertyannotation__ecbviolations_last30",
            "propertyannotation__ecbviolations_lastyear",
            "propertyannotation__ecbviolations_last3years",
            "propertyannotation__ecbviolations_lastupdated",
            "propertyannotation__housinglitigations_last30",
            "propertyannotation__housinglitigations_lastyear",
            "propertyannotation__housinglitigations_last3years",
            "propertyannotation__housinglitigations_lastupdated",
            "propertyannotation__dobfiledpermits_last30",
            "propertyannotation__dobfiledpermits_lastyear",
            "propertyannotation__dobfiledpermits_last3years",
            "propertyannotation__dobfiledpermits_lastupdated",
            "propertyannotation__dobissuedpermits_last30",
            "propertyannotation__dobissuedpermits_lastyear",
            "propertyannotation__dobissuedpermits_last3years",
            "propertyannotation__dobissuedpermits_lastupdated",
            "propertyannotation__evictions_last30",
            "propertyannotation__evictions_lastyear",
            "propertyannotation__evictions_last3years",
            "propertyannotation__evictions_lastupdated",
            "propertyannotation__acrisrealmasters_last30",
            "propertyannotation__acrisrealmasters_lastyear",
            "propertyannotation__acrisrealmasters_last3years",
            "propertyannotation__acrisrealmasters_lastupdated",
            "propertyannotation__foreclosures_last30",
            "propertyannotation__foreclosures_lastyear",
            "propertyannotation__foreclosures_last3years",
            "propertyannotation__foreclosures_lastupdated",
            "propertyannotation__legalclassa")

        return queryset
