from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Student, Teacher


@login_required
def students(request):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    has_permission = request.user.groups.filter(
        name__in=allowed_roles
    ).exists()

    if not has_permission:
        return render(
            request,
            "accounts/access_denied.html",
        )

    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    if is_product_owner:
        student_list = Student.objects.all()
    else:
        student_list = Student.objects.filter(
            tenant=request.user.tenant
        )

    context = {
        "students": student_list,
    }

    return render(
        request,
        "accounts/students.html",
        context,
    )

@login_required
def teachers(request):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    has_permission = request.user.groups.filter(
        name__in=allowed_roles
    ).exists()

    if not has_permission:
        return render(
            request,
            "accounts/access_denied.html",
        )

    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    if is_product_owner:
        teacher_list = Teacher.objects.all()
    else:
        teacher_list = Teacher.objects.filter(
            tenant=request.user.tenant
        )

    context = {
        "teachers": teacher_list,
    }

    return render(
        request,
        "accounts/teachers.html",
        context,
    )