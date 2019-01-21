from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import NestedRouterMixin

from datasets import views as v

council_housingtype_summary = v.council_views.CouncilViewSet.as_view({
    'get': 'housingtype_summary',
})
council_properties = v.council_views.CouncilViewSet.as_view({
    'get': 'properties',
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

router.register(r'properties', v.property_views.PropertyViewSet)
router.register(r'buildings', v.building_views.BuildingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('councils/<int:pk>/housingtype-summary', council_housingtype_summary, name='council-housingtype-summary'),
    # path('councils/<int:pk>/properties/', council_properties, name='council-properties'),
]
