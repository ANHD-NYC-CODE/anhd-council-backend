from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import NestedRouterMixin
from rest_framework import renderers

from datasets import views as v

council_summary = v.council_views.CouncilViewSet.as_view({
    'get': 'council_summary',
})

community_summary = v.community_views.CommunityViewSet.as_view({
    'get': 'community_summary',
})


property_buildings_summary = v.property_views.PropertyViewSet.as_view({
    'get': 'buildings_summary',
})

property_housing_type_summary = v.property_views.PropertyViewSet.as_view({
    'get': 'housing_type_summary',
})

building_search = v.search_views.SearchViewSet.as_view({
    'get': 'building_search',
})

property_bbls = v.property_views.PropertyViewSet.as_view({
    'post': 'property_bbls'
})


class NestedDefaultRouter(NestedRouterMixin, DefaultRouter):
    pass


router = NestedDefaultRouter()
councils_router = router.register(r'councils', v.council_views.CouncilViewSet)

councils_router.register(
    'properties',
    v.property_views.PropertyViewSet,
    base_name='council-properties',
    parents_query_lookups=['council']
)

communities_router = router.register(r'communities', v.community_views.CommunityViewSet)

communities_router.register(
    'properties',
    v.property_views.PropertyViewSet,
    base_name='community-properties',
    parents_query_lookups=['cd']
)

properties_router = router.register(r'properties', v.property_views.PropertyViewSet)
properties_router.register(
    'buildings',
    v.building_views.BuildingViewSet,
    base_name='property-buildings',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'hpdbuildings',
    v.hpdbuilding_views.HPDBuildingViewSet,
    base_name='property-hpdbuildings',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'hpdviolations',
    v.hpdviolation_views.HPDViolationViewSet,
    base_name='property-hpdviolations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'hpdcomplaints',
    v.hpdcomplaint_views.HPDComplaintViewSet,
    base_name='property-hpdcomplaints',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'hpdproblems',
    v.hpdproblem_views.HPDProblemViewSet,
    base_name='property-hpdproblems',
    parents_query_lookups=['complaintid__bbl']
)

properties_router.register(
    'dobviolations',
    v.dobviolation_views.DOBViolationViewSet,
    base_name='property-dobviolations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobcomplaints',
    v.dobcomplaint_views.DOBComplaintViewSet,
    base_name='property-dobcomplaints',
    parents_query_lookups=['bin__bbl']
)

properties_router.register(
    'ecbviolations',
    v.ecbviolation_views.ECBViolationViewSet,
    base_name='property-ecbviolations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'acrisrealmasters',
    v.acrisrealmaster_views.AcrisRealMasterViewSet,
    base_name='property-acrisrealmasters',
    parents_query_lookups=['acrisreallegal__bbl']
)

properties_router.register(
    'evictions',
    v.eviction_views.EvictionViewSet,
    base_name='property-evictions',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'housinglitigations',
    v.housinglitigation_views.HousingLitigationViewSet,
    base_name='property-housinglitigations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'hpdregistrations',
    v.hpdregistration_views.HPDRegistrationViewSet,
    base_name='property-hpdregistrations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'taxliens',
    v.taxlien_views.TaxLienViewSet,
    base_name='property-taxliens',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'conhrecords',
    v.conhrecord_views.CONHRecordViewSet,
    base_name='property-conhrecords',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'taxbills',
    v.rentstabilizationrecord_views.RentStabilizationRecordViewSet,
    base_name='property-taxbills',
    parents_query_lookups=['ucbbl']
)

properties_router.register(
    'subsidyj51',
    v.subsidyj51_views.SubsidyJ51ViewSet,
    base_name='property-subsidyj51',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'subsidy421a',
    v.subsidy421a_views.Subsidy421aViewSet,
    base_name='property-subsidy421a',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'coredata',
    v.coresubsidyrecord_views.CoreSubsidyRecordViewSet,
    base_name='property-coredata',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobpermitissuedlegacy',
    v.dobpermitissuedlegacy_views.DOBPermitIssuedLegacyViewSet,
    base_name='property-dobpermitissuedlegacy',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobpermitissuednow',
    v.dobpermitissuednow_views.DOBPermitIssuedNowViewSet,
    base_name='property-dobpermitissuednow',
    parents_query_lookups=['bbl']
)


properties_router.register(
    'dobissuedpermits',
    v.dobissuedpermit_view.DOBIssuedPermitViewSet,
    base_name='property-dobissuedpermits',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobfiledpermits',
    v.dobfiledpermit_view.DOBFiledPermitViewSet,
    base_name='property-dobfiledpermits',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'doblegacyfiledpermits',
    v.doblegacyfiledpermit_views.DOBLegacyFiledPermitViewSet,
    base_name='property-doblegacyfiledpermit',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobnowfiledpermits',
    v.dobnowfiledpermit_views.DOBNowFiledPermitViewSet,
    base_name='property-dobnowfiledpermit',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'publichousingrecords',
    v.publichousingrecord_views.PublicHousingRecordViewSet,
    base_name='property-publichousingrecords',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'lispendens',
    v.lispenden_views.LisPendenViewSet,
    base_name='property-lispendens',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'propertyannotations',
    v.propertyannotation_views.PropertyAnnotationViewSet,
    base_name='property-propertyannotations',
    parents_query_lookups=['bbl']
)


buildings_router = router.register(r'buildings', v.building_views.BuildingViewSet)

buildings_router.register(
    'hpdviolations',
    v.hpdviolation_views.HPDViolationViewSet,
    base_name='building-hpdviolations',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'hpdcomplaints',
    v.hpdcomplaint_views.HPDComplaintViewSet,
    base_name='building-hpdcomplaints',
    parents_query_lookups=['bin']
)


buildings_router.register(
    'dobviolations',
    v.dobviolation_views.DOBViolationViewSet,
    base_name='building-dobviolations',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobcomplaints',
    v.dobcomplaint_views.DOBComplaintViewSet,
    base_name='building-dobcomplaints',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'ecbviolations',
    v.ecbviolation_views.ECBViolationViewSet,
    base_name='building-ecbviolations',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'housinglitigations',
    v.housinglitigation_views.HousingLitigationViewSet,
    base_name='building-housinglitigations',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'hpdregistrations',
    v.hpdregistration_views.HPDRegistrationViewSet,
    base_name='building-hpdregistrations',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobpermitissuedlegacy',
    v.dobpermitissuedlegacy_views.DOBPermitIssuedLegacyViewSet,
    base_name='building-dobpermitissuedlegacy',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobpermitissuednow',
    v.dobpermitissuednow_views.DOBPermitIssuedNowViewSet,
    base_name='building-dobpermitissuednow',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobissuedpermits',
    v.dobissuedpermit_view.DOBIssuedPermitViewSet,
    base_name='building-dobissuedpermits',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobfiledpermits',
    v.dobfiledpermit_view.DOBFiledPermitViewSet,
    base_name='building-dobfiledpermits',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'doblegacyfiledpermits',
    v.doblegacyfiledpermit_views.DOBLegacyFiledPermitViewSet,
    base_name='building-doblegacyfiledpermits',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobnowfiledpermits',
    v.dobnowfiledpermit_views.DOBNowFiledPermitViewSet,
    base_name='building-dobnowfiledpermits',
    parents_query_lookups=['bin']
)


buildings_router.register(
    'conhrecords',
    v.taxlien_views.TaxLienViewSet,
    base_name='building-conhrecords',
    parents_query_lookups=['bin']
)


hpdbuildings_router = router.register(r'hpdbuildings', v.hpdbuilding_views.HPDBuildingViewSet)

hpdbuildings_router.register(
    'hpdviolations',
    v.hpdviolation_views.HPDViolationViewSet,
    base_name='building-hpdviolations',
    parents_query_lookups=['buildingid']
)

hpdbuildings_router.register(
    'hpdcomplaints',
    v.hpdcomplaint_views.HPDComplaintViewSet,
    base_name='building-hpdcomplaints',
    parents_query_lookups=['buildingid']
)

hpdbuildings_router.register(
    'housinglitigations',
    v.housinglitigation_views.HousingLitigationViewSet,
    base_name='building-housinglitigations',
    parents_query_lookups=['buildingid']
)

hpdbuildings_router.register(
    'hpdregistrations',
    v.hpdregistration_views.HPDRegistrationViewSet,
    base_name='building-hpdregistrations',
    parents_query_lookups=['buildingid']
)

router.register(r'hpdviolations', v.hpdviolation_views.HPDViolationViewSet)
hpdcomplaints_router = router.register(r'hpdcomplaints', v.hpdcomplaint_views.HPDComplaintViewSet)
hpdcomplaints_router.register(
    'hpdproblems',
    v.hpdproblem_views.HPDProblemViewSet,
    base_name='building-hpdproblems',
    parents_query_lookups=['complaintid']
)

router.register(r'hpdproblems', v.hpdproblem_views.HPDProblemViewSet)
router.register(r'dobviolations', v.dobviolation_views.DOBViolationViewSet)
router.register(r'dobcomplaints', v.dobcomplaint_views.DOBComplaintViewSet)
router.register(r'ecbviolations', v.ecbviolation_views.ECBViolationViewSet)
acrisrealmasters_router = router.register(r'acrisrealmasters', v.acrisrealmaster_views.AcrisRealMasterViewSet)

acrisrealmasters_router.register(
    'acrisreallegals',
    v.acrisreallegal_views.AcrisRealLegalViewSet,
    base_name='acrisrealmaster-acrisreallegals',
    parents_query_lookups=['documentid']
)


acrisrealmasters_router.register(
    'acrisrealparties',
    v.acrisrealparty_views.AcrisRealPartyViewSet,
    base_name='acrisrealmaster-acrisrealparties',
    parents_query_lookups=['documentid']
)

router.register(r'acrisreallegals', v.acrisreallegal_views.AcrisRealLegalViewSet)
router.register(r'acrisrealparties', v.acrisrealparty_views.AcrisRealPartyViewSet)
router.register(r'evictions', v.eviction_views.EvictionViewSet)
router.register(r'housinglitigations', v.housinglitigation_views.HousingLitigationViewSet)
hpdregistrations_router = router.register(r'hpdregistrations', v.hpdregistration_views.HPDRegistrationViewSet)
hpdregistrations_router.register(
    'hpdcontacts',
    v.hpdcontact_views.HPDContactViewSet,
    base_name='hpdregistration-hpdcontacts',
    parents_query_lookups=['registrationid']
)
router.register(r'hpdcontacts', v.hpdcontact_views.HPDContactViewSet)
router.register(r'taxliens', v.taxlien_views.TaxLienViewSet)
router.register(r'conhrecords', v.conhrecord_views.CONHRecordViewSet)
router.register(r'taxbills', v.rentstabilizationrecord_views.RentStabilizationRecordViewSet)
router.register(r'subsidyj51', v.subsidyj51_views.SubsidyJ51ViewSet)
router.register(r'subsidy421a', v.subsidy421a_views.Subsidy421aViewSet)
router.register(r'coredata', v.coresubsidyrecord_views.CoreSubsidyRecordViewSet)
router.register(r'dobpermitissuedlegacy', v.dobpermitissuedlegacy_views.DOBPermitIssuedLegacyViewSet)
router.register(r'dobpermitissuednow', v.dobpermitissuednow_views.DOBPermitIssuedNowViewSet)
router.register(r'dobissuedpermits', v.dobissuedpermit_view.DOBIssuedPermitViewSet)
router.register(r'dobfiledpermits', v.dobfiledpermit_view.DOBFiledPermitViewSet)
router.register(r'doblegacyfiledpermits', v.doblegacyfiledpermit_views.DOBLegacyFiledPermitViewSet)
router.register(r'dobnowfiledpermits', v.dobnowfiledpermit_views.DOBNowFiledPermitViewSet)
router.register(r'publichousingrecords', v.publichousingrecord_views.PublicHousingRecordViewSet)
router.register(r'lispendens', v.lispenden_views.LisPendenViewSet)
router.register(r'propertyannotations', v.propertyannotation_views.PropertyAnnotationViewSet)

custom_routes = format_suffix_patterns([
    path('councils/<int:pk>/summary/', council_summary, name='council-summary'),
    path('communities/<int:pk>/summary/', community_summary, name='community-summary'),
    path('search/buildings/', building_search, name='buildings-search'),
    path('bbls', property_bbls, name='property-bbls')
])

urlpatterns = [
    *custom_routes,
    path('', include(router.urls)),
]
