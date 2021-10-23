from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from users import views as v

router = routers.DefaultRouter()
router.register(r'user-requests', v.UserRequestViewSet)


current_user = v.UserViewSet.as_view({
    'get': 'get_current_user',
})

custom_routes = format_suffix_patterns([
    path('users/current/', current_user, name='users-current'),
])

urlpatterns = [
    *custom_routes,
    path('', include(router.urls)),

    path('users/bookmarks/', v.UserBookmarkedPropertyCollection.as_view()),
    path('users/bookmarks/<uuid:pk>/', v.UserBookmarkedPropertyMember.as_view()),

    # User Custom Searches
    path('users/customsearches/', v.UserCustomSearchCollection.as_view()),
    path('users/customsearches/<uuid:pk>/', v.UserCustomSearchMember.as_view()),
]
