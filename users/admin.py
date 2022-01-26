from django.contrib import admin
from django.utils.safestring import mark_safe


# Register your models here.
# from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from users.models import CustomUser, CustomSearch, UserCustomSearch, UserRequest, AccessRequest, UserBookmarkedProperty, DistrictDashboard, UserDistrictDashboard
from users.forms import CustomUserChangeForm, CustomUserCreationForm
from app.tasks import async_update_custom_search_result_hash
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect

from django.contrib.admin import AdminSite
from django.urls import path

# JWT
# https://simpleisbetterthancomplex.com/tutorial/2018/12/19/how-to-use-jwt-authentication-with-django-rest-framework.html


class UserRequestAdmin(admin.ModelAdmin):
    def response_change(self, request, obj):
        if "_approve-request" in request.POST:
            obj.approve()
            messages.info(request,
                          "This request has been approved and a registration email has been sent including a generated password.")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    list_display = ('email', 'username', 'first_name', 'last_name',
                    'organization', 'description', 'long_description', 'approved', 'date_created')

    list_filter = ('approved', 'email', 'organization',
                   'description', 'date_created')

    search_fields = ('approved', 'organization', 'email', 'description')

    ordering = ['-date_created']
    readonly_fields = ('email', 'username', 'first_name', 'last_name',
                       'organization', 'description', 'long_description', 'approved', 'date_created')
    actions = []


class AccessRequestAdmin(admin.ModelAdmin):
    def response_change(self, request, obj):
        if "_approve-request" in request.POST:
            obj.approve()
            messages.info(request,
                          "This request has been approved and a registration email has been sent including a generated password.")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    def requestor_username(self, obj):
        if obj.user:
            return obj.user.username
        else:
            return 'Error no user'
    requestor_username.allow_tags = True
    requestor_username.short_description = 'Requestor Username'

    def user_link(self, obj):
        if obj.user:
            url = f'/admin/users/customuser/{obj.user.id}/change/'
            link = f'<a href="{url}">{obj.user.username}</a>'
            return mark_safe(link)
        else:
            return 'Error no user'

    list_display = ('requestor_username', 'access_type', 'organization_email', 'organization', 'position', 'description', 'approved', 'date_created')

    list_filter = ('approved', 'organization_email', 'organization',
                   'description', 'date_created')

    search_fields = ('approved', 'organization', 'organization_email', 'description')

    ordering = ['-date_created']
    readonly_fields = ('access_type', 'organization', 'position',
                       'description', 'approved', 'date_created', 'user_link')
    actions = []


def add_user_to_trusted(modeladmin, request, queryset):
    trusted_group = Group.objects.get(name='trusted')
    for user in queryset:
        trusted_group.user_set.add(user)
add_user_to_trusted.short_description = 'Adds user to trusted'

def remove_user_to_trusted(modeladmin, request, queryset):
    trusted_group = Group.objects.get(name='trusted')
    for user in queryset:
        trusted_group.user_set.remove(user)
remove_user_to_trusted.short_description = 'Removes user to trusted'

class CustomUserAdmin(auth_admin.UserAdmin):
    def get_urls(self):
        urls = super(CustomUserAdmin, self).get_urls()
        password_url = [
            path('<str:id>/change/password/',
                 self.admin_site.admin_view(self.user_change_password), name='admin-user-change-password'),
        ]
        return password_url + urls

    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Groups'

    def request_status(self, obj):
        try:
            access_request = obj.accessrequest
            url = f'/admin/users/accessrequest/{access_request.id}/change/'
            status = 'Approved' if access_request.approved else 'Pending'
            link = f'<a href="{url}">{status}</a>'
            return mark_safe(link)
        except AccessRequest.DoesNotExist:
            return 'No request'
    request_status.allow_tags = True
    request_status.short_description = 'Request Status'

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'request_status'
                                    )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    limited_fieldsets = (
        (None, {'fields': ('email', 'username')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username')}
         ),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = auth_admin.AdminPasswordChangeForm
    list_display = ('email', 'username', 'first_name',
                    'last_name', 'is_superuser', 'request_status',
                    'group')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined', 'request_status')
    actions = [add_user_to_trusted, remove_user_to_trusted]


@admin.register(UserBookmarkedProperty)
class UserBookmarkedPropertyAdmin(admin.ModelAdmin):
    pass


@admin.register(DistrictDashboard)
class DistrictDashboardAdmin(admin.ModelAdmin):
    pass

@admin.register(UserDistrictDashboard)
class UserDistrictDashboardAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomSearch)
class CustomSearchAdmin(admin.ModelAdmin):
    def response_change(self, request, obj):
        if "_update-result-hash" in request.POST:
            async_update_custom_search_result_hash.delay(obj.id)

            messages.info(request,
                          "Updating result hash now, may take minute please leave this page and come back")

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


@admin.register(UserCustomSearch)
class UserCustomSearchAdmin(admin.ModelAdmin):
    pass

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserRequest, UserRequestAdmin)
admin.site.register(AccessRequest, AccessRequestAdmin)
