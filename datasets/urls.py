from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import NestedRouterMixin

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

router.register(r'buildings', v.building_views.BuildingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('councils/<int:pk>/housingtype-summary/', council_housingtype_summary, name='council-housingtype-summary'),
    path('properties/<str:pk>/buildings-summary/', property_buildings_summary, name='property-buildings-summary'),
]
