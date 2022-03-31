from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _


class UserAdmin(BaseUserAdmin):

    ordering = ['id']
    list_display = ['email', 'name']

    # this is for user change view
    # I should see the effect 
    fieldsets = (
        (_('Credentials'), {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'), 
        {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important Dates'), {'fields': ('last_login',)})
    )

    # this is for user creation view
    # seems like gettext or (_) was not necessary! why?!
    add_fieldsets = (
        (_('Credentials'), {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.register(models.User, UserAdmin)