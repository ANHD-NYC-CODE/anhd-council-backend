from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import NestedRouterMixin
from rest_framework import renderers

from datasets import views as v

council_housingtype_summary = v.council_views.CouncilViewSet.as_view({
    'get': 'housingtype_summary',
})

property_buildings_summary = v.property_views.PropertyViewSet.as_view({
    'get': 'buildings_summary',
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
    parents_query_lookups=['buildingid__bin']
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


router.register(r'hpdbuildings', v.hpdbuilding_views.HPDBuildingViewSet)
router.register(r'hpdviolations', v.hpdviolation_views.HPDViolationViewSet)
router.register(r'hpdcomplaints', v.hpdcomplaint_views.HPDComplaintViewSet)
router.register(r'dobviolations', v.dobviolation_views.DOBViolationViewSet)
router.register(r'dobcomplaints', v.dobcomplaint_views.DOBComplaintViewSet)
router.register(r'ecbviolations', v.ecbviolation_views.ECBViolationViewSet)
acrisrealmasters_router = router.register(r'acrisrealmasters', v.acrisrealmaster_views.AcrisRealMasterViewSet)

acrisrealmasters_router.register(
    'acrisrealparties',
    v.acrisrealparty_views.AcrisRealPartyViewSet,
    base_name='acrisrealmaster-acrisrealparties',
    parents_query_lookups=['documentid']
)

router.register(r'acrisreallegals', v.acrisreallegal_views.AcrisRealLegalViewSet)
router.register(r'acrisrealparties', v.acrisrealparty_views.AcrisRealPartyViewSet)

custom_routes = format_suffix_patterns([
    path('councils/<int:pk>/housingtype-summary/', council_housingtype_summary, name='council-housingtype-summary'),
    path('properties/<str:pk>/buildings-summary/', property_buildings_summary, name='property-buildings-summary'),
])

urlpatterns = [
    path('', include(router.urls)),
    *custom_routes
]
