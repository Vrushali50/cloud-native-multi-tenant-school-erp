from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import TenantForm, SchoolAdminCreationForm
from .models import Tenant


def is_product_owner(user):

    return user.groups.filter(
        name="Product Owner"
    ).exists()


@login_required
def platform_schools(request):

    if not is_product_owner(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    search_query = request.GET.get("q", "")

    schools = Tenant.objects.all().order_by(
        "id"
    )

    if search_query:

        schools = schools.filter(
            school_name__icontains=search_query
        )

    total_schools = schools.count()

    active_schools = schools.filter(
        is_active=True
    ).count()

    inactive_schools = schools.filter(
        is_active=False
    ).count()

    context = {
        "schools": schools,
        "search_query": search_query,
        "total_schools": total_schools,
        "active_schools": active_schools,
        "inactive_schools": inactive_schools,
    }

    return render(
        request,
        "tenants/platform_schools.html",
        context,
    )


@login_required
def add_school(request):

    if not is_product_owner(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":

        form = TenantForm(
            request.POST,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "School created successfully.",
            )

            return redirect(
                "tenants:platform_schools"
            )

    else:

        form = TenantForm()

    context = {
        "form": form,
        "title": "Add School",
        "button_text": "Save School",
    }

    return render(
        request,
        "tenants/school_form.html",
        context,
    )


@login_required
def edit_school(request, school_id):

    if not is_product_owner(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    school = get_object_or_404(
        Tenant,
        id=school_id,
    )

    if request.method == "POST":

        form = TenantForm(
            request.POST,
            instance=school,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "School updated successfully.",
            )

            return redirect(
                "tenants:platform_schools"
            )

    else:

        form = TenantForm(
            instance=school,
        )

    context = {
        "form": form,
        "title": "Edit School",
        "button_text": "Update School",
    }

    return render(
        request,
        "tenants/school_form.html",
        context,
    )


@login_required
@login_required
def toggle_school_status(request, school_id):

    if not is_product_owner(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    school = get_object_or_404(
        Tenant,
        id=school_id,
    )

    school.is_active = not school.is_active

    if hasattr(school, "status"):

        if school.is_active:

            school.status = "Active"

        else:

            school.status = "Suspended"

    school.save()

    if school.is_active:

        messages.success(
            request,
            "School activated successfully.",
        )

    else:

        messages.warning(
            request,
            "School suspended successfully.",
        )

    return redirect(
        "tenants:platform_schools"
    )


@login_required
def school_admins(request):

    if not is_product_owner(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    User = get_user_model()

    search_query = request.GET.get("q", "")

    admins = User.objects.filter(
        groups__name="School Admin"
    ).select_related(
        "tenant"
    ).order_by(
        "tenant",
        "username",
    )

    if search_query:

        admins = admins.filter(
            username__icontains=search_query
        )

    context = {
        "admins": admins,
        "search_query": search_query,
    }

    return render(
        request,
        "tenants/school_admins.html",
        context,
    )


@login_required
def add_school_admin(request):

    if not is_product_owner(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":

        form = SchoolAdminCreationForm(
            request.POST,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "School Admin user created successfully.",
            )

            return redirect(
                "tenants:school_admins"
            )

    else:

        form = SchoolAdminCreationForm()

    context = {
        "form": form,
        "title": "Create School Admin",
        "button_text": "Create School Admin",
    }

    return render(
        request,
        "tenants/school_admin_form.html",
        context,
    )