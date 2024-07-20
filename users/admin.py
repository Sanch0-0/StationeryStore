from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

from .forms import UserCreationForm

admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "full_name")
    list_display_links = ("id", "email", "full_name")
    search_fields = ("id", "email", "full_name")
    ordering = ("id", "email")
    readonly_fields = ("date_joined", "last_login")
    add_form = UserCreationForm
    fieldsets = [
        (
            "User's data",
            {
                'fields': ("email", "full_name", "date_joined", "last_login")
            }
        )
    ]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
