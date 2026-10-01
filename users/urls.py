from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from users import views as v
from users.mfa import views as mfa_views

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
    path('api/auth/mfa/totp/verify/', mfa_views.MFATotpVerifyView.as_view()),
    path('api/auth/mfa/totp/setup/begin/', mfa_views.MFATotpSetupBeginView.as_view()),
    path('api/auth/mfa/totp/setup/confirm/', mfa_views.MFATotpSetupConfirmView.as_view()),
    path('api/auth/mfa/passkey/register/begin/', mfa_views.MFAPasskeyRegisterBeginView.as_view()),
    path('api/auth/mfa/passkey/register/complete/', mfa_views.MFAPasskeyRegisterCompleteView.as_view()),
    path('api/auth/mfa/passkey/authenticate/begin/', mfa_views.MFAPasskeyAuthenticateBeginView.as_view()),
    path('api/auth/mfa/passkey/authenticate/complete/', mfa_views.MFAPasskeyAuthenticateCompleteView.as_view()),
    path('api/auth/mfa/passkeys/', mfa_views.MFAPasskeyListView.as_view()),
    path('api/auth/mfa/passkeys/<int:pk>/', mfa_views.MFAPasskeyDetailView.as_view()),
    path('api/auth/mfa/status/', mfa_views.MFAStatusView.as_view()),
    path('', include(router.urls)),

    path('users/register/', v.UserRegisterView.as_view(), name='signup'),
    path('users/access-request/', v.AccessRequestCollection.as_view()),
    path('users/verify/<str:username>/<str:verification_token>/', v.UserVerifyView.as_view()),

    path('users/bookmarks/', v.UserBookmarkedPropertyCollection.as_view()),
    path('users/bookmarks/<uuid:pk>/', v.UserBookmarkedPropertyMember.as_view()),

    # User Custom Searches
    path('users/customsearches/', v.UserCustomSearchCollection.as_view()),
    path('users/customsearches/<uuid:pk>/', v.UserCustomSearchMember.as_view()),
]
