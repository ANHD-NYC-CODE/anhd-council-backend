from django.contrib import admin

# Register your models here.
# from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from users.models import CustomUser, UserRequest
from users.forms import CustomUserChangeForm, CustomUserCreationForm
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


# @admin.action(description='Adds user to trusted')
def add_user_to_trusted(modeladmin, request, queryset):
    trusted_group = Group.objects.get(name='trusted')
    for user in queryset:
        trusted_group.user_set.add(user)
add_user_to_trusted.short_description = 'Adds user to trusted'

# @admin.action(description='Removes user to trusted')
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
                    'last_name', 'is_superuser', 'group')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined',)
    actions = [add_user_to_trusted, remove_user_to_trusted]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserRequest, UserRequestAdmin)
