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
        (
            None, 
            {'fields': (
                'email', 
                'password'
                )
            }
        ),
        (
            ('Permissiones'),
            {'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser'
            )}
        ),
        (
            ('Important Dates'),
            {'fields': (
                'last_login', 
            )}
        )
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None,
        {'fields':
            (
                'email', 
                'password1', 
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }
        ),
    )

admin.site.register(models.User, UserAdmin)