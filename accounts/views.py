from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import transaction
from tenants.models import Tenant

from core.models import (
    Student,
    Teacher,
    TeacherSubject,
    StudentAttendance,
    SchoolClass,
    Subject,
    Examination,
    Result,
    StudentFee,
    FeePayment,
    Book,
    LibraryIssue,
    Announcement,
)

from .forms import UserForm, EditUserForm


User = get_user_model()


class UserLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        return reverse_lazy(
            "accounts:dashboard"
        )


@login_required
def dashboard(request):

    user = request.user

    is_product_owner = user.groups.filter(
        name="Product Owner"
    ).exists()

    is_school_admin = user.groups.filter(
        name="School Admin"
    ).exists()

    is_teacher = user.groups.filter(
        name="Teacher"
    ).exists()

    is_student = user.groups.filter(
        name="Student"
    ).exists()

    is_accountant = user.groups.filter(
        name="Accountant"
    ).exists()

    is_librarian = user.groups.filter(
        name="Librarian"
    ).exists()

    role_name = "No Role"

    if user.groups.exists():
        role_name = user.groups.first().name

    today = timezone.localdate()

    if is_product_owner:

        total_schools = Tenant.objects.count()

        active_schools = 0
        inactive_schools = 0

        if hasattr(Tenant, "is_active"):

            active_schools = Tenant.objects.filter(
                is_active=True
            ).count()

            inactive_schools = Tenant.objects.filter(
                is_active=False
            ).count()

        context = {
            "role_name": role_name,

            "is_product_owner": is_product_owner,
            "is_school_admin": is_school_admin,
            "is_teacher": is_teacher,
            "is_student": is_student,
            "is_accountant": is_accountant,
            "is_librarian": is_librarian,

            "total_schools": total_schools,
            "active_schools": active_schools,
            "inactive_schools": inactive_schools,

            "dashboard_announcements": Announcement.objects.none(),
        }

        return render(
            request,
            "accounts/dashboard.html",
            context,
        )

    tenant = user.tenant

    if tenant is None:
        return render(
            request,
            "accounts/access_denied.html",
        )

    dashboard_announcements = Announcement.objects.filter(
        tenant=tenant,
        is_active=True,
        start_date__lte=today,
    ).filter(
        Q(end_date__isnull=True)
        | Q(end_date__gte=today)
    )

    if not is_school_admin:

        dashboard_announcements = dashboard_announcements.filter(
            Q(target_role="All")
            | Q(target_role=role_name)
        )

    dashboard_announcements = dashboard_announcements.select_related(
        "created_by"
    ).order_by(
        "-created_at"
    )[:5]

    total_schools = 0

    students = Student.objects.filter(
        tenant=tenant
    )

    teachers = Teacher.objects.filter(
        tenant=tenant
    )

    classes = SchoolClass.objects.filter(
        tenant=tenant
    )

    subjects = Subject.objects.filter(
        tenant=tenant
    )

    examinations = Examination.objects.filter(
        tenant=tenant
    )

    results = Result.objects.filter(
        tenant=tenant
    )

    student_fees = StudentFee.objects.filter(
        tenant=tenant
    )

    fee_payments = FeePayment.objects.filter(
        student_fee__tenant=tenant
    )

    books = Book.objects.filter(
        tenant=tenant
    )

    library_issues = LibraryIssue.objects.filter(
        tenant=tenant
    )

    total_students = students.count()

    active_students = students.filter(
        is_active=True
    ).count()

    total_teachers = teachers.count()

    active_teachers = teachers.filter(
        is_active=True
    ).count()

    total_classes = classes.count()

    total_subjects = subjects.count()

    total_exams = examinations.count()

    upcoming_exams = examinations.filter(
        exam_date__gte=today
    ).order_by(
        "exam_date",
        "start_time",
    )[:5]

    published_results = results.filter(
        is_published=True
    ).count()

    pass_results = results.filter(
        result_status="PASS"
    ).count()

    fail_results = results.filter(
        result_status="FAIL"
    ).count()

    latest_results = results.select_related(
        "student",
        "academic_term",
    ).order_by(
        "-updated_at"
    )[:5]

    total_fee_assigned = (
        student_fees.aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0.00")
    )

    total_fee_collected = (
        student_fees.aggregate(
            total=Sum("paid_amount")
        )["total"]
        or Decimal("0.00")
    )

    total_fee_pending = Decimal("0.00")

    for fee in student_fees:
        total_fee_pending = total_fee_pending + fee.balance_amount

    pending_fee_count = student_fees.filter(
        status="Pending"
    ).count()

    partial_fee_count = student_fees.filter(
        status="Partially Paid"
    ).count()

    paid_fee_count = student_fees.filter(
        status="Paid"
    ).count()

    total_payments = fee_payments.count()

    fee_collection_percent = 0

    if total_fee_assigned > 0:

        fee_collection_percent = round(
            float(total_fee_collected / total_fee_assigned * 100),
            1,
        )

    recent_fee_records = student_fees.select_related(
        "student",
        "fee_structure",
    ).order_by(
        "-updated_at"
    )[:5]

    total_books = books.count()

    total_book_copies = (
        books.aggregate(
            total=Sum("total_copies")
        )["total"]
        or 0
    )

    available_book_copies = (
        books.aggregate(
            total=Sum("available_copies")
        )["total"]
        or 0
    )

    borrowed_books = library_issues.filter(
        status="Borrowed"
    ).count()

    returned_books = library_issues.filter(
        status="Returned"
    ).count()

    total_library_fines = (
        library_issues.aggregate(
            total=Sum("fine_amount")
        )["total"]
        or Decimal("0.00")
    )

    borrowed_records = library_issues.filter(
        status="Borrowed"
    ).select_related(
        "book",
        "student",
        "teacher",
    ).order_by(
        "due_date"
    )[:5]

    teacher_profile = None
    teacher_assignment_count = 0
    teacher_subject_count = 0
    teacher_upcoming_exams = Examination.objects.none()
    teacher_library_records = LibraryIssue.objects.none()

    if is_teacher:

        teacher_profile = Teacher.objects.filter(
            user=user
        ).first()

        if teacher_profile:

            teacher_assignments = TeacherSubject.objects.filter(
                teacher=teacher_profile
            ).select_related(
                "subject",
                "school_class",
                "section",
                "academic_year",
            )

            teacher_assignment_count = teacher_assignments.count()

            teacher_subject_count = teacher_assignments.values(
                "subject"
            ).distinct().count()

            teacher_subjects = teacher_assignments.values_list(
                "subject",
                flat=True,
            )

            teacher_upcoming_exams = Examination.objects.filter(
                tenant=tenant,
                subject_id__in=teacher_subjects,
                exam_date__gte=today,
            ).order_by(
                "exam_date",
                "start_time",
            )[:5]

            teacher_library_records = LibraryIssue.objects.filter(
                tenant=tenant,
                teacher=teacher_profile,
            ).select_related(
                "book",
            ).order_by(
                "-issue_date",
            )[:5]

    student_profile = None
    student_fee_total = Decimal("0.00")
    student_fee_paid = Decimal("0.00")
    student_fee_pending = Decimal("0.00")
    student_borrowed_books = 0
    student_results_count = 0
    student_upcoming_exams = Examination.objects.none()
    student_recent_fees = StudentFee.objects.none()
    student_library_records = LibraryIssue.objects.none()

    if is_student:

        student_profile = Student.objects.filter(
            user=user
        ).first()

        if student_profile:

            student_fee_qs = StudentFee.objects.filter(
                tenant=tenant,
                student=student_profile,
            ).select_related(
                "fee_structure",
            )

            student_fee_total = (
                student_fee_qs.aggregate(
                    total=Sum("total_amount")
                )["total"]
                or Decimal("0.00")
            )

            student_fee_paid = (
                student_fee_qs.aggregate(
                    total=Sum("paid_amount")
                )["total"]
                or Decimal("0.00")
            )

            for fee in student_fee_qs:
                student_fee_pending = student_fee_pending + fee.balance_amount

            student_recent_fees = student_fee_qs.order_by(
                "-updated_at"
            )[:5]

            student_borrowed_books = LibraryIssue.objects.filter(
                tenant=tenant,
                student=student_profile,
                status="Borrowed",
            ).count()

            student_library_records = LibraryIssue.objects.filter(
                tenant=tenant,
                student=student_profile,
            ).select_related(
                "book",
            ).order_by(
                "-issue_date",
            )[:5]

            student_results_count = Result.objects.filter(
                tenant=tenant,
                student=student_profile,
                is_published=True,
            ).count()

            if student_profile.school_class:

                student_upcoming_exams = Examination.objects.filter(
                    tenant=tenant,
                    school_class=student_profile.school_class,
                    exam_date__gte=today,
                    is_published=True,
                ).order_by(
                    "exam_date",
                    "start_time",
                )[:5]

    context = {
        "role_name": role_name,

        "is_product_owner": is_product_owner,
        "is_school_admin": is_school_admin,
        "is_teacher": is_teacher,
        "is_student": is_student,
        "is_accountant": is_accountant,
        "is_librarian": is_librarian,

        "dashboard_announcements": dashboard_announcements,

        "total_schools": total_schools,

        "total_students": total_students,
        "active_students": active_students,
        "total_teachers": total_teachers,
        "active_teachers": active_teachers,
        "total_classes": total_classes,
        "total_subjects": total_subjects,

        "total_exams": total_exams,
        "upcoming_exams": upcoming_exams,
        "published_results": published_results,
        "pass_results": pass_results,
        "fail_results": fail_results,
        "latest_results": latest_results,

        "total_fee_assigned": total_fee_assigned,
        "total_fee_collected": total_fee_collected,
        "total_fee_pending": total_fee_pending,
        "pending_fee_count": pending_fee_count,
        "partial_fee_count": partial_fee_count,
        "paid_fee_count": paid_fee_count,
        "total_payments": total_payments,
        "fee_collection_percent": fee_collection_percent,
        "recent_fee_records": recent_fee_records,

        "total_books": total_books,
        "total_book_copies": total_book_copies,
        "available_book_copies": available_book_copies,
        "borrowed_books": borrowed_books,
        "returned_books": returned_books,
        "total_library_fines": total_library_fines,
        "borrowed_records": borrowed_records,

        "teacher_profile": teacher_profile,
        "teacher_assignment_count": teacher_assignment_count,
        "teacher_subject_count": teacher_subject_count,
        "teacher_upcoming_exams": teacher_upcoming_exams,
        "teacher_library_records": teacher_library_records,

        "student_profile": student_profile,
        "student_fee_total": student_fee_total,
        "student_fee_paid": student_fee_paid,
        "student_fee_pending": student_fee_pending,
        "student_borrowed_books": student_borrowed_books,
        "student_results_count": student_results_count,
        "student_upcoming_exams": student_upcoming_exams,
        "student_recent_fees": student_recent_fees,
        "student_library_records": student_library_records,
    }

    return render(
        request,
        "accounts/dashboard.html",
        context,
    )


@login_required
def user_list(request):

    has_permission = request.user.groups.filter(
        name="School Admin"
    ).exists()

    if not has_permission:

        return render(
            request,
            "accounts/access_denied.html",
        )

    users = User.objects.select_related(
        "tenant"
    ).filter(
        tenant=request.user.tenant
    )

    search = request.GET.get("search", "")
    role = request.GET.get("role", "")

    if search:

        users = users.filter(
            username__icontains=search
        )

    if role:

        users = users.filter(
            groups__name=role
        )

    context = {
        "users": users,
        "search": search,
        "selected_role": role,
    }

    return render(
        request,
        "accounts/user_list.html",
        context,
    )


@login_required
def add_user(request):

    has_permission = request.user.groups.filter(
        name="School Admin"
    ).exists()

    if not has_permission:

        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":

        form = UserForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            try:

                with transaction.atomic():

                    form.save()

                messages.success(
                    request,
                    "User created successfully."
                )

                return redirect(
                    "accounts:user_list"
                )

            except Exception as error:

                messages.error(
                    request,
                    f"User could not be created. Error: {error}"
                )

    else:

        form = UserForm(
            current_user=request.user,
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "accounts/add_user.html",
        context,
    )

@login_required
def edit_user(request, user_id):

    has_permission = request.user.groups.filter(
        name="School Admin"
    ).exists()

    if not has_permission:

        return render(
            request,
            "accounts/access_denied.html",
        )

    selected_user = get_object_or_404(
        User,
        id=user_id,
        tenant=request.user.tenant,
    )

    if request.method == "POST":

        form = EditUserForm(
            request.POST,
            instance=selected_user,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "User changes saved successfully."
            )

            return redirect(
                "accounts:user_list"
            )

    else:

        form = EditUserForm(
            instance=selected_user,
            current_user=request.user,
        )

    context = {
        "form": form,
        "selected_user": selected_user,
    }

    return render(
        request,
        "accounts/edit_user.html",
        context,
    )


@login_required
def toggle_user_status(request, user_id):

    has_permission = request.user.groups.filter(
        name="School Admin"
    ).exists()

    if not has_permission:

        return render(
            request,
            "accounts/access_denied.html",
        )

    selected_user = get_object_or_404(
        User,
        id=user_id,
        tenant=request.user.tenant,
    )

    selected_user.is_active = not selected_user.is_active
    selected_user.save()

    if selected_user.is_active:

        messages.success(
            request,
            "User activated successfully."
        )

    else:

        messages.success(
            request,
            "User deactivated successfully."
        )

    return redirect(
        "accounts:user_list"
    )


@login_required
def teacher_dashboard(request):

    is_teacher = request.user.groups.filter(
        name="Teacher"
    ).exists()

    if not is_teacher:

        return render(
            request,
            "accounts/access_denied.html",
        )

    try:

        teacher = request.user.teacher_profile

    except Teacher.DoesNotExist:

        teacher = None

    assignments = TeacherSubject.objects.none()
    attendance_count = 0

    if teacher:

        assignments = TeacherSubject.objects.filter(
            teacher=teacher
        ).select_related(
            "subject",
            "school_class",
            "section",
            "academic_year",
        )

        attendance_count = StudentAttendance.objects.filter(
            teacher_subject__teacher=teacher
        ).count()

    context = {
        "teacher": teacher,
        "assignments": assignments,
        "assignment_count": assignments.count(),
        "attendance_count": attendance_count,
    }

    return render(
        request,
        "accounts/teacher_dashboard.html",
        context,
    )


@login_required
def student_dashboard(request):

    is_student = request.user.groups.filter(
        name="Student"
    ).exists()

    if not is_student:

        return render(
            request,
            "accounts/access_denied.html",
        )

    try:

        student = request.user.student_profile

    except Student.DoesNotExist:

        student = None

    attendance_count = 0

    if student:

        attendance_count = StudentAttendance.objects.filter(
            student=student
        ).count()

    context = {
        "student": student,
        "attendance_count": attendance_count,
    }

    return render(
        request,
        "accounts/student_dashboard.html",
        context,
    )