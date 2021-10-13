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

    path('users/bookmarks/', v.UserBookmarkedPropertiesCollection.as_view()),
    path('users/bookmarks/<uuid:pk>', v.UserBookmarkedPropertiesMember.as_view()),
]
