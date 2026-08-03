from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from.models import User

@admin.register(User)
class CustomerUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "tenant",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "tenant",
        "is_active",
        "is_staff",
        "groups",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "ERP Information",
            {
                "fields":(
                    "tenant",
                    "phone",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "ERP Information",
            {
                "fields": (
                    "email",
                    "tenant",
                    "phone",
                )
            },
        ),
    )


