from django.urls import path

from .views import (
    platform_schools,
    add_school,
    edit_school,
    toggle_school_status,
    school_admins,
    add_school_admin,
)

app_name = "tenants"

urlpatterns = [
    path(
        "schools/",
        platform_schools,
        name="platform_schools",
    ),

    path(
        "schools/add/",
        add_school,
        name="add_school",
    ),

    path(
        "schools/<int:school_id>/edit/",
        edit_school,
        name="edit_school",
    ),

    path(
        "schools/<int:school_id>/toggle-status/",
        toggle_school_status,
        name="toggle_school_status",
    ),

    path(
        "school-admins/",
        school_admins,
        name="school_admins",
    ),

    path(
        "school-admins/add/",
        add_school_admin,
        name="add_school_admin",
    ),
]