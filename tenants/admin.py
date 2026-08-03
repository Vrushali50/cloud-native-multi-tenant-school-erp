from django.contrib import admin
from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = (
        "school_name",
        "subdomain",
        "subscription_plan",
        "status",
        "contact_email",
        "created_at",
    )

    list_filter = (
        "subscription_plan",
        "status",
    )

    search_fields = (
        "school_name",
        "subdomain",
        "contact_email",    
    )
