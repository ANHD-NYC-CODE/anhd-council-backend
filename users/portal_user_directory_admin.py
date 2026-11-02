import csv
from datetime import datetime

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html

from users.models import PortalUserDirectory


def _format_admin_datetime(value):
    if not value:
        return ''
    from django.utils import timezone as dj_tz
    if dj_tz.is_aware(value):
        value = dj_tz.localtime(value)
    return value.strftime('%Y-%m-%d %H:%M')


@admin.register(PortalUserDirectory)
class PortalUserDirectoryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/users/portaluserdirectory/change_list.html'

    show_full_result_count = False
    list_per_page = 100
    list_max_show_all = 200

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'date_joined_display',
        'last_login_display',
        'login_count',
        'is_active',
        'group_names',
        'access_organization',
        'access_type',
        'access_approved',
        'edit_user_link',
    )
    list_filter = ('is_active', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(is_staff=False, is_superuser=False)
            .select_related('accessrequest')
            .prefetch_related('groups')
        )

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path(
                'export-csv/',
                self.admin_site.admin_view(self.export_csv_view),
                name='users_portaluserdirectory_export_csv',
            ),
        ]
        return extra + urls

    @admin.display(description='Signed up', ordering='date_joined')
    def date_joined_display(self, obj):
        return _format_admin_datetime(obj.date_joined)

    @admin.display(description='Last login', ordering='last_login')
    def last_login_display(self, obj):
        return _format_admin_datetime(obj.last_login)

    @admin.display(description='Groups')
    def group_names(self, obj):
        return ', '.join(g.name for g in obj.groups.all())

    @admin.display(description='Organization')
    def access_organization(self, obj):
        try:
            return obj.accessrequest.organization or ''
        except ObjectDoesNotExist:
            return ''

    @admin.display(description='Access type')
    def access_type(self, obj):
        try:
            return obj.accessrequest.access_type or ''
        except ObjectDoesNotExist:
            return ''

    @admin.display(description='Access approved', boolean=True)
    def access_approved(self, obj):
        try:
            return bool(obj.accessrequest.approved)
        except ObjectDoesNotExist:
            return False

    @admin.display(description='Account')
    def edit_user_link(self, obj):
        url = f'/admin/users/customuser/{obj.pk}/change/'
        return format_html('<a href="{}">Open</a>', url)

    def export_csv_view(self, request):
        cl = self.get_changelist_instance(request)
        queryset = cl.get_queryset(request)

        filename = f'portal-users-{datetime.utcnow().strftime("%Y%m%d")}.csv'
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([
            'email',
            'username',
            'first_name',
            'last_name',
            'date_joined',
            'last_login',
            'login_count',
            'is_active',
            'groups',
            'access_type',
            'organization',
            'access_approved',
            'access_request_date',
        ])

        for user in queryset.iterator(chunk_size=500):
            try:
                access = user.accessrequest
                access_type = access.access_type or ''
                organization = access.organization or ''
                access_approved = access.approved
                access_date = access.date_created
            except ObjectDoesNotExist:
                access_type = organization = ''
                access_approved = False
                access_date = None

            writer.writerow([
                user.email,
                user.username,
                user.first_name,
                user.last_name,
                _format_admin_datetime(user.date_joined),
                _format_admin_datetime(user.last_login),
                user.login_count,
                user.is_active,
                ', '.join(g.name for g in user.groups.all()),
                access_type,
                organization,
                access_approved,
                _format_admin_datetime(access_date),
            ])

        return response
