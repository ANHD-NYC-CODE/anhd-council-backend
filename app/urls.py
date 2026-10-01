"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path as url
# from django.conf.urls import url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views

from rest_framework_simplejwt import views as jwt_views

from datasets import views as datasets
from users.mfa.views import MFATokenObtainPairView
from users.mfa.admin_views import (
    AdminMfaEnrollView,
    AdminMfaLoginView,
    AdminMfaPasskeyAuthBeginView,
    AdminMfaPasskeyAuthCompleteView,
    AdminMfaPasskeyRegisterBeginView,
    AdminMfaPasskeyRegisterCompleteView,
    AdminMfaSettingsPasskeyDeleteView,
    AdminMfaSettingsPasskeyRegisterBeginView,
    AdminMfaSettingsPasskeyRegisterCompleteView,
    AdminMfaSettingsPasskeyRenameView,
    AdminMfaSettingsView,
    AdminMfaVerifyView,
)

urlpatterns = [
    path('admin/login/', AdminMfaLoginView.as_view()),
    path('admin/mfa/verify/', AdminMfaVerifyView.as_view(), name='admin_mfa_verify'),
    path('admin/mfa/enroll/', AdminMfaEnrollView.as_view(), name='admin_mfa_enroll'),
    path(
        'admin/mfa/passkey/authenticate/begin/',
        AdminMfaPasskeyAuthBeginView.as_view(),
        name='admin_mfa_passkey_auth_begin',
    ),
    path(
        'admin/mfa/passkey/authenticate/complete/',
        AdminMfaPasskeyAuthCompleteView.as_view(),
        name='admin_mfa_passkey_auth_complete',
    ),
    path(
        'admin/mfa/passkey/register/begin/',
        AdminMfaPasskeyRegisterBeginView.as_view(),
        name='admin_mfa_passkey_register_begin',
    ),
    path(
        'admin/mfa/passkey/register/complete/',
        AdminMfaPasskeyRegisterCompleteView.as_view(),
        name='admin_mfa_passkey_register_complete',
    ),
    path('admin/mfa/settings/', AdminMfaSettingsView.as_view(), name='admin_mfa_settings'),
    path(
        'admin/mfa/settings/passkey/register/begin/',
        AdminMfaSettingsPasskeyRegisterBeginView.as_view(),
        name='admin_mfa_settings_passkey_register_begin',
    ),
    path(
        'admin/mfa/settings/passkey/register/complete/',
        AdminMfaSettingsPasskeyRegisterCompleteView.as_view(),
        name='admin_mfa_settings_passkey_register_complete',
    ),
    path(
        'admin/mfa/settings/passkeys/<int:pk>/rename/',
        AdminMfaSettingsPasskeyRenameView.as_view(),
        name='admin_mfa_settings_passkey_rename',
    ),
    path(
        'admin/mfa/settings/passkeys/<int:pk>/delete/',
        AdminMfaSettingsPasskeyDeleteView.as_view(),
        name='admin_mfa_settings_passkey_delete',
    ),
    path('admin/', admin.site.urls),
    # path('docs/', ...) — disabled: coreapi incompatible with Python 3.12 (missing pkg_resources)
    path('api/token/', MFATokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    url('^', include('django.contrib.auth.urls')),
    path('', include('datasets.urls')),
    path('', include('users.urls')),
    path('', include('core.urls')),


]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns + staticfiles_urlpatterns()
