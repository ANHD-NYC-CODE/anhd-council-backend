from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

from users.mfa import policy


class AdminMfaMiddleware:
    """Require completed MFA for staff Django admin sessions (same rules as API login)."""

    EXEMPT_PREFIXES = (
        '/admin/login',
        '/admin/logout',
        '/admin/mfa/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.startswith('/admin/') and not any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
            user = request.user
            if user.is_authenticated and user.is_staff:
                if policy.user_requires_mfa_enrollment(user):
                    logout(request)
                    return redirect(reverse('admin:login'))
                if policy.user_has_mfa_enabled(user) and not request.session.get('admin_mfa_verified'):
                    logout(request)
                    return redirect(reverse('admin:login'))
        return self.get_response(request)
