from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from .models import ProxyGroup, ProxyPermission, User


# Register your models here.
class UserAdmin(BaseUserAdmin):
    """
    docstring for UserAdmin.
    """

    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {
            'fields': (
                ('created_at', 'updated_at'),
                'email',
                'password'
            )
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_volunteer',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined'
            )
        }),
    )
    list_display = ('email', 'is_staff', 'is_superuser')
    ordering = ('email', )
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(User, UserAdmin)


admin.site.unregister(Group)
admin.site.register(ProxyGroup, GroupAdmin)
