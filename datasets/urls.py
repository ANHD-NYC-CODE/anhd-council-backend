from django.urls import path, re_path as url, include
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
    basename='council-properties',
    parents_query_lookups=['council']
)

communities_router = router.register(
    r'communities', v.community_views.CommunityViewSet)

communities_router.register(
    'properties',
    v.property_views.PropertyViewSet,
    basename='community-properties',
    parents_query_lookups=['cd']
)

zipcodes_router = router.register(r'zipcodes', v.zipcode_views.ZipCodeViewSet)

zipcodes_router.register(
    'properties',
    v.property_views.PropertyViewSet,
    basename='zipcode-properties',
    parents_query_lookups=['zipcode']
)

stateassembly_router = router.register(
    r'stateassemblies', v.stateassembly_views.StateAssemblyViewSet)

stateassembly_router.register(
    'properties',
    v.property_views.PropertyViewSet,
    basename='stateassembly-properties',
    parents_query_lookups=['stateassembly']
)

statesenate_router = router.register(
    r'statesenates', v.statesenate_views.StateSenateViewSet)

statesenate_router.register(
    'properties',
    v.property_views.PropertyViewSet,
    basename='statesenate-properties',
    parents_query_lookups=['statesenate']
)

properties_router = router.register(
    r'properties', v.property_views.PropertyViewSet)

properties_router.register(
    'buildings',
    v.building_views.BuildingViewSet,
    basename='property-buildings',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'padrecords',
    v.padrecord_views.PadRecordViewSet,
    basename='property-padrecords',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'addressrecords',
    v.addressrecord_views.AddressRecordViewSet,
    basename='property-addressrecords',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'hpdbuildings',
    v.hpdbuilding_views.HPDBuildingViewSet,
    basename='property-hpdbuildings',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'aepbuildings',
    v.aepbuilding_views.AEPBuildingViewSet,
    basename='property-aepbuildings',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'hpdviolations',
    v.hpdviolation_views.HPDViolationViewSet,
    basename='property-hpdviolations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'hpdcomplaints',
    v.hpdcomplaint_views.HPDComplaintViewSet,
    basename='property-hpdcomplaints',
    parents_query_lookups=['bbl']
)


properties_router.register(
    'dobviolations',
    v.dobviolation_views.DOBViolationViewSet,
    basename='property-dobviolations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobcomplaints',
    v.dobcomplaint_views.DOBComplaintViewSet,
    basename='property-dobcomplaints',
    parents_query_lookups=['bin__bbl']
)

properties_router.register(
    'ecbviolations',
    v.ecbviolation_views.ECBViolationViewSet,
    basename='property-ecbviolations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'acrisrealmasters',
    v.acrisrealmaster_views.AcrisRealMasterViewSet,
    basename='property-acrisrealmasters',
    parents_query_lookups=['acrisreallegal__bbl']
)

properties_router.register(
    'evictions',
    v.eviction_views.EvictionViewSet,
    basename='property-evictions',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'housinglitigations',
    v.housinglitigation_views.HousingLitigationViewSet,
    basename='property-housinglitigations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'hpdregistrations',
    v.hpdregistration_views.HPDRegistrationViewSet,
    basename='property-hpdregistrations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'taxliens',
    v.taxlien_views.TaxLienViewSet,
    basename='property-taxliens',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'conhrecords',
    v.conhrecord_views.CONHRecordViewSet,
    basename='property-conhrecords',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'taxbills',
    v.rentstabilizationrecord_views.RentStabilizationRecordViewSet,
    basename='property-taxbills',
    parents_query_lookups=['ucbbl']
)

properties_router.register(
    'subsidyj51',
    v.subsidyj51_views.SubsidyJ51ViewSet,
    basename='property-subsidyj51',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'subsidy421a',
    v.subsidy421a_views.Subsidy421aViewSet,
    basename='property-subsidy421a',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'coredata',
    v.coresubsidyrecord_views.CoreSubsidyRecordViewSet,
    basename='property-coredata',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobpermitissuedlegacy',
    v.dobpermitissuedlegacy_views.DOBPermitIssuedLegacyViewSet,
    basename='property-dobpermitissuedlegacy',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobpermitissuednow',
    v.dobpermitissuednow_views.DOBPermitIssuedNowViewSet,
    basename='property-dobpermitissuednow',
    parents_query_lookups=['bbl']
)


properties_router.register(
    'dobissuedpermits',
    v.dobissuedpermit_view.DOBIssuedPermitViewSet,
    basename='property-dobissuedpermits',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobfiledpermits',
    v.dobfiledpermit_view.DOBFiledPermitViewSet,
    basename='property-dobfiledpermits',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'doblegacyfiledpermits',
    v.doblegacyfiledpermit_views.DOBLegacyFiledPermitViewSet,
    basename='property-doblegacyfiledpermit',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'dobnowfiledpermits',
    v.dobnowfiledpermit_views.DOBNowFiledPermitViewSet,
    basename='property-dobnowfiledpermit',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'publichousingrecords',
    v.publichousingrecord_views.PublicHousingRecordViewSet,
    basename='property-publichousingrecords',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'lispendens',
    v.lispenden_views.LisPendenViewSet,
    basename='property-lispendens',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'foreclosures',
    v.foreclosure_views.ForeclosureViewSet,
    basename='property-foreclosures',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'foreclosure-auctions',
    v.foreclosureauction_views.ForeclosureAuctionViewSet,
    basename='property-foreclosure-auctions',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'propertyannotations',
    v.propertyannotation_views.PropertyAnnotationViewSet,
    basename='property-propertyannotations',
    parents_query_lookups=['bbl']
)

properties_router.register(
    'ocahousingcourts',
    v.ocahousingcourt_views.OCAHousingCourtViewSet,
    basename='property-ocahousingcourts',
    parents_query_lookups=['bbl']
)


buildings_router = router.register(
    r'buildings', v.building_views.BuildingViewSet)
buildings_router.register(
    'padrecords',
    v.padrecord_views.PadRecordViewSet,
    basename='building-padrecords',
    parents_query_lookups=['bin']
)
buildings_router.register(
    'hpdviolations',
    v.hpdviolation_views.HPDViolationViewSet,
    basename='building-hpdviolations-bin',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'hpdcomplaints',
    v.hpdcomplaint_views.HPDComplaintViewSet,
    basename='building-hpdcomplaints-bin',
    parents_query_lookups=['bin']
)


buildings_router.register(
    'dobviolations',
    v.dobviolation_views.DOBViolationViewSet,
    basename='building-dobviolations',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobcomplaints',
    v.dobcomplaint_views.DOBComplaintViewSet,
    basename='building-dobcomplaints',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'ecbviolations',
    v.ecbviolation_views.ECBViolationViewSet,
    basename='building-ecbviolations',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'housinglitigations',
    v.housinglitigation_views.HousingLitigationViewSet,
    basename='building-housinglitigations-bin',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'hpdregistrations',
    v.hpdregistration_views.HPDRegistrationViewSet,
    basename='building-hpdregistrations-bin',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobpermitissuedlegacy',
    v.dobpermitissuedlegacy_views.DOBPermitIssuedLegacyViewSet,
    basename='building-dobpermitissuedlegacy',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobpermitissuednow',
    v.dobpermitissuednow_views.DOBPermitIssuedNowViewSet,
    basename='building-dobpermitissuednow',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobissuedpermits',
    v.dobissuedpermit_view.DOBIssuedPermitViewSet,
    basename='building-dobissuedpermits',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobfiledpermits',
    v.dobfiledpermit_view.DOBFiledPermitViewSet,
    basename='building-dobfiledpermits',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'doblegacyfiledpermits',
    v.doblegacyfiledpermit_views.DOBLegacyFiledPermitViewSet,
    basename='building-doblegacyfiledpermits',
    parents_query_lookups=['bin']
)

buildings_router.register(
    'dobnowfiledpermits',
    v.dobnowfiledpermit_views.DOBNowFiledPermitViewSet,
    basename='building-dobnowfiledpermits',
    parents_query_lookups=['bin']
)


buildings_router.register(
    'conhrecords',
    v.taxlien_views.TaxLienViewSet,
    basename='building-conhrecords',
    parents_query_lookups=['bin']
)


hpdbuildings_router = router.register(
    r'hpdbuildings', v.hpdbuilding_views.HPDBuildingViewSet)

hpdbuildings_router.register(
    'hpdviolations',
    v.hpdviolation_views.HPDViolationViewSet,
    basename='building-hpdviolations-buildingid',
    parents_query_lookups=['buildingid']
)

hpdbuildings_router.register(
    'hpdcomplaints',
    v.hpdcomplaint_views.HPDComplaintViewSet,
    basename='building-hpdcomplaints-buildingid',
    parents_query_lookups=['buildingid']
)

hpdbuildings_router.register(
    'housinglitigations',
    v.housinglitigation_views.HousingLitigationViewSet,
    basename='building-housinglitigations-buildingid',
    parents_query_lookups=['buildingid']
)

hpdbuildings_router.register(
    'hpdregistrations',
    v.hpdregistration_views.HPDRegistrationViewSet,
    basename='building-hpdregistrations-buildingid',
    parents_query_lookups=['buildingid']
)

router.register(r'hpdviolations', v.hpdviolation_views.HPDViolationViewSet)
router.register(r'hpdcomplaints', v.hpdcomplaint_views.HPDComplaintViewSet)
router.register(r'dobviolations', v.dobviolation_views.DOBViolationViewSet)
router.register(r'dobcomplaints', v.dobcomplaint_views.DOBComplaintViewSet)
router.register(r'ecbviolations', v.ecbviolation_views.ECBViolationViewSet)
router.register(r'aepbuildings', v.aepbuilding_views.AEPBuildingViewSet)

acrisrealmasters_router = router.register(
    r'acrisrealmasters', v.acrisrealmaster_views.AcrisRealMasterViewSet)

acrisrealmasters_router.register(
    'acrisreallegals',
    v.acrisreallegal_views.AcrisRealLegalViewSet,
    basename='acrisrealmaster-acrisreallegals',
    parents_query_lookups=['documentid']
)


acrisrealmasters_router.register(
    'acrisrealparties',
    v.acrisrealparty_views.AcrisRealPartyViewSet,
    basename='acrisrealmaster-acrisrealparties',
    parents_query_lookups=['documentid']
)

router.register(r'acrisreallegals',
                v.acrisreallegal_views.AcrisRealLegalViewSet)
router.register(r'acrisrealparties',
                v.acrisrealparty_views.AcrisRealPartyViewSet)
router.register(r'evictions', v.eviction_views.EvictionViewSet)
router.register(r'housinglitigations',
                v.housinglitigation_views.HousingLitigationViewSet)
hpdregistrations_router = router.register(
    r'hpdregistrations', v.hpdregistration_views.HPDRegistrationViewSet)
hpdregistrations_router.register(
    'hpdcontacts',
    v.hpdcontact_views.HPDContactViewSet,
    basename='hpdregistration-hpdcontacts',
    parents_query_lookups=['registrationid']
)
router.register(r'hpdcontacts', v.hpdcontact_views.HPDContactViewSet)
router.register(r'taxliens', v.taxlien_views.TaxLienViewSet)
router.register(r'conhrecords', v.conhrecord_views.CONHRecordViewSet)
router.register(
    r'taxbills', v.rentstabilizationrecord_views.RentStabilizationRecordViewSet)
router.register(r'subsidyj51', v.subsidyj51_views.SubsidyJ51ViewSet)
router.register(r'subsidy421a', v.subsidy421a_views.Subsidy421aViewSet)
router.register(
    r'coredata', v.coresubsidyrecord_views.CoreSubsidyRecordViewSet)
router.register(r'dobpermitissuedlegacy',
                v.dobpermitissuedlegacy_views.DOBPermitIssuedLegacyViewSet)
router.register(r'dobpermitissuednow',
                v.dobpermitissuednow_views.DOBPermitIssuedNowViewSet)
router.register(r'dobissuedpermits',
                v.dobissuedpermit_view.DOBIssuedPermitViewSet)
router.register(r'dobfiledpermits',
                v.dobfiledpermit_view.DOBFiledPermitViewSet)
router.register(r'doblegacyfiledpermits',
                v.doblegacyfiledpermit_views.DOBLegacyFiledPermitViewSet)
router.register(r'dobnowfiledpermits',
                v.dobnowfiledpermit_views.DOBNowFiledPermitViewSet)
router.register(r'publichousingrecords',
                v.publichousingrecord_views.PublicHousingRecordViewSet)
router.register(r'lispendens', v.lispenden_views.LisPendenViewSet)
router.register(r'foreclosures', v.foreclosure_views.ForeclosureViewSet)
router.register(r'foreclosure-auctions',
                v.foreclosureauction_views.ForeclosureAuctionViewSet)
router.register(r'propertyannotations',
                v.propertyannotation_views.PropertyAnnotationViewSet)
router.register(r'addressrecords', v.addressrecord_views.AddressRecordViewSet)
router.register(r'padrecords', v.padrecord_views.PadRecordViewSet)
router.register(r'ocahousingcourts',
                v.ocahousingcourt_views.OCAHousingCourtViewSet)


custom_routes = format_suffix_patterns([
    path('councils/<int:pk>/summary/', council_summary, name='council-summary'),
    path('communities/<int:pk>/summary/',
         community_summary, name='community-summary'),
    path('search/buildings/', building_search, name='buildings-search'),
    path('bbls', property_bbls, name='property-bbls')
])

urlpatterns = [
    *custom_routes,
    path('', include(router.urls)),
]
