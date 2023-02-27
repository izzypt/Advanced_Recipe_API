"""
Django Admin costumazition
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            ('Permissions'),
            {'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser'
            )}
        )
    )

admin.site.register(models.User, UserAdmin)