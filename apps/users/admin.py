from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from .models import User
from .forms import UserCreationForm

admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "username", "email", "is_active", "is_staff")
    list_display_links = ("id", "username", "email")
    search_fields = ("id", "username", "email")
    ordering = ("id", "email", "full_name")
    readonly_fields = ("date_joined", "last_login")
    
    fieldsets = [
        (
            "User's data",
            {
                'fields': (
                    "username", "email", "full_name", "mobile_phone", "avatar", 
                    "place_of_delivery", "postal_code", "country", "password",
                    "date_joined", "last_login"
                )
            }
        ),
        (
            "Permissions",
            {
                'fields': ("is_staff", "is_active", "is_superuser")
            }
        )
    ]

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )