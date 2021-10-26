from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from users.models import CustomUser, CustomSearch, UserCustomSearch, UserRequest, UserBookmarkedProperty, DistrictDashboard, UserDistrictDashboard
from users.forms import CustomUserChangeForm, CustomUserCreationForm
from core.tasks import async_update_custom_search_result_hash
from django.contrib import messages
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


class CustomUserAdmin(auth_admin.UserAdmin):
    def get_urls(self):
        urls = super(CustomUserAdmin, self).get_urls()
        password_url = [
            path('<str:id>/change/password/',
                 self.admin_site.admin_view(self.user_change_password), name='admin-user-change-password'),
        ]
        return password_url + urls

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
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
                    'last_name', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined',)


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
