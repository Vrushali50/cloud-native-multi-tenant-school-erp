from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from decimal import Decimal
from .forms import AcademicYearForm, SchoolClassForm, SectionForm, SubjectForm, TeacherSubjectForm, StudentForm, TeacherForm, StaffAttendanceForm, TimetableForm, ExaminationForm, ExamHallAllocationForm, StudentMarkForm, ResultForm, FeeStructureForm, StudentFeeForm, FeePaymentForm, BulkStudentFeeAssignForm, BookCategoryForm, BookForm, LibraryIssueForm, ReturnBookForm, AnnouncementForm, AcademicTermForm
from .models import Student, Teacher, AcademicYear, SchoolClass, Section, Subject, TeacherSubject, StudentAttendance, StaffAttendance, Timetable, AcademicTerm, Examination, ExamHallAllocation, StudentMark, Result, FeeStructure, StudentFee, FeePayment, BookCategory, Book, LibraryIssue, Announcement
from django.utils import timezone
from datetime import datetime
from django.db.models import Q, Sum
from django import forms

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
        student_list = Student.objects.select_related(
            "tenant",
            "school_class",
            "section",
        ).all()
    else:
        student_list = Student.objects.select_related(
            "tenant",
            "school_class",
            "section",
        ).filter(
            tenant=request.user.tenant
        )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:
        from django.db.models import Q

        student_list = student_list.filter(
            Q(student_id__icontains=search)
            | Q(admission_number__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )

    context = {
        "students": student_list,
        "search": search,
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

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    if is_product_owner:
        teacher_list = Teacher.objects.select_related(
            "tenant"
        ).all()
    else:
        teacher_list = Teacher.objects.select_related(
            "tenant"
        ).filter(
            tenant=request.user.tenant
        )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:
        from django.db.models import Q

        teacher_list = teacher_list.filter(
            Q(teacher_id__icontains=search)
            | Q(employee_number__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )

    return render(
        request,
        "accounts/teachers.html",
        {
            "teachers": teacher_list,
            "search": search,
        },
    )


@login_required
def academic_years(request):
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
        academic_year_list = AcademicYear.objects.all()
    else:
        academic_year_list = AcademicYear.objects.filter(
            tenant=request.user.tenant
        )

    context = {
        "academic_years": academic_year_list,
    }

    return render(
        request,
        "accounts/academic_years.html",
        context,
    )


@login_required
def add_academic_year(request):
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

    if request.method == "POST":
        form = AcademicYearForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Academic year created successfully."
            )

            return redirect(
                "core:academic_years"
            )

    else:
        form = AcademicYearForm(
            current_user=request.user,
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "accounts/add_academic_year.html",
        context,
    )


@login_required
def edit_academic_year(request, academic_year_id):
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
        academic_year = get_object_or_404(
            AcademicYear,
            id=academic_year_id,
        )
    else:
        academic_year = get_object_or_404(
            AcademicYear,
            id=academic_year_id,
            tenant=request.user.tenant,
        )

    if request.method == "POST":
        form = AcademicYearForm(
            request.POST,
            instance=academic_year,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Academic year updated successfully."
            )

            return redirect(
                "core:academic_years"
            )

    else:
        form = AcademicYearForm(
            instance=academic_year,
            current_user=request.user,
        )

    context = {
        "form": form,
        "academic_year": academic_year,
    }

    return render(
        request,
        "accounts/edit_academic_year.html",
        context,
    )
def can_manage_academic_terms(user):

    return user.groups.filter(
        name="School Admin"
    ).exists()


@login_required
def academic_terms(request):

    if not can_manage_academic_terms(request.user):

        return render(
            request,
            "accounts/access_denied.html",
        )

    search_query = request.GET.get("q", "")
    year_filter = request.GET.get("academic_year", "")

    terms = AcademicTerm.objects.select_related(
        "academic_year",
    ).filter(
        academic_year__tenant=request.user.tenant,
    ).order_by(
        "-academic_year__year_name",
        "start_date",
    )

    academic_years = AcademicYear.objects.filter(
        tenant=request.user.tenant,
    )

    if search_query:

        terms = terms.filter(
            Q(term_name__icontains=search_query)
            | Q(academic_year__year_name__icontains=search_query)
        )

    if year_filter:

        terms = terms.filter(
            academic_year_id=year_filter
        )

    context = {
        "terms": terms,
        "academic_years": academic_years,
        "search_query": search_query,
        "year_filter": year_filter,
    }

    return render(
        request,
        "core/academic_terms.html",
        context,
    )


@login_required
def add_academic_term(request):

    if not can_manage_academic_terms(request.user):

        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":

        form = AcademicTermForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Academic term created successfully.",
            )

            return redirect(
                "core:academic_terms"
            )

    else:

        form = AcademicTermForm(
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Add Academic Term",
        "button_text": "Save Term",
    }

    return render(
        request,
        "core/academic_term_form.html",
        context,
    )


@login_required
def edit_academic_term(request, term_id):

    if not can_manage_academic_terms(request.user):

        return render(
            request,
            "accounts/access_denied.html",
        )

    term = get_object_or_404(
        AcademicTerm,
        id=term_id,
        academic_year__tenant=request.user.tenant,
    )

    if request.method == "POST":

        form = AcademicTermForm(
            request.POST,
            instance=term,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Academic term updated successfully.",
            )

            return redirect(
                "core:academic_terms"
            )

    else:

        form = AcademicTermForm(
            instance=term,
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Edit Academic Term",
        "button_text": "Update Term",
    }

    return render(
        request,
        "core/academic_term_form.html",
        context,
    )


@login_required
def set_current_academic_term(request, term_id):

    if not can_manage_academic_terms(request.user):

        return render(
            request,
            "accounts/access_denied.html",
        )

    term = get_object_or_404(
        AcademicTerm,
        id=term_id,
        academic_year__tenant=request.user.tenant,
    )

    AcademicTerm.objects.filter(
        academic_year=term.academic_year,
    ).update(
        is_current=False
    )

    term.is_current = True
    term.save()

    messages.success(
        request,
        "Academic term set as current successfully.",
    )

    return redirect(
        "core:academic_terms"
    )
@login_required
def classes(request):
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
        class_list = SchoolClass.objects.select_related(
            "tenant",
            "academic_year",
        ).all()
    else:
        class_list = SchoolClass.objects.select_related(
            "tenant",
            "academic_year",
        ).filter(
            tenant=request.user.tenant
        )

    context = {
        "classes": class_list,
    }

    return render(
        request,
        "accounts/classes.html",
        context,
    )


@login_required
def add_class(request):
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

    if request.method == "POST":
        form = SchoolClassForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Class created successfully."
            )

            return redirect(
                "core:classes"
            )

    else:
        form = SchoolClassForm(
            current_user=request.user,
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "accounts/add_class.html",
        context,
    )


@login_required
def edit_class(request, class_id):
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
        school_class = get_object_or_404(
            SchoolClass,
            id=class_id,
        )
    else:
        school_class = get_object_or_404(
            SchoolClass,
            id=class_id,
            tenant=request.user.tenant,
        )

    if request.method == "POST":
        form = SchoolClassForm(
            request.POST,
            instance=school_class,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Class updated successfully."
            )

            return redirect(
                "core:classes"
            )

    else:
        form = SchoolClassForm(
            instance=school_class,
            current_user=request.user,
        )

    context = {
        "form": form,
        "school_class": school_class,
    }

    return render(
        request,
        "accounts/edit_class.html",
        context,
    )

@login_required
def sections(request):
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
        section_list = Section.objects.select_related(
            "school_class",
            "school_class__tenant",
            "school_class__academic_year",
        ).all()
    else:
        section_list = Section.objects.select_related(
            "school_class",
            "school_class__tenant",
            "school_class__academic_year",
        ).filter(
            school_class__tenant=request.user.tenant
        )

    context = {
        "sections": section_list,
    }

    return render(
        request,
        "accounts/sections.html",
        context,
    )

@login_required
def add_section(request):
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

    if request.method == "POST":
        form = SectionForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Section created successfully."
            )

            return redirect(
                "core:sections"
            )

    else:
        form = SectionForm(
            current_user=request.user,
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "accounts/add_section.html",
        context,
    )

@login_required
def edit_section(request, section_id):
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
        section = get_object_or_404(
            Section,
            id=section_id,
        )
    else:
        section = get_object_or_404(
            Section,
            id=section_id,
            school_class__tenant=request.user.tenant,
        )

    if request.method == "POST":
        form = SectionForm(
            request.POST,
            instance=section,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Section updated successfully."
            )

            return redirect(
                "core:sections"
            )

    else:
        form = SectionForm(
            instance=section,
            current_user=request.user,
        )

    context = {
        "form": form,
        "section": section,
    }

    return render(
        request,
        "accounts/edit_section.html",
        context,
    )
@login_required
def subjects(request):
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
        subject_list = Subject.objects.select_related(
            "tenant"
        ).all()
    else:
        subject_list = Subject.objects.select_related(
            "tenant"
        ).filter(
            tenant=request.user.tenant
        )

    context = {
        "subjects": subject_list,
    }

    return render(
        request,
        "accounts/subjects.html",
        context,
    )


@login_required
def add_subject(request):
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

    if request.method == "POST":
        form = SubjectForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Subject created successfully."
            )

            return redirect(
                "core:subjects"
            )

    else:
        form = SubjectForm(
            current_user=request.user,
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "accounts/add_subject.html",
        context,
    )


@login_required
def edit_subject(request, subject_id):
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
        subject = get_object_or_404(
            Subject,
            id=subject_id,
        )
    else:
        subject = get_object_or_404(
            Subject,
            id=subject_id,
            tenant=request.user.tenant,
        )

    if request.method == "POST":
        form = SubjectForm(
            request.POST,
            instance=subject,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Subject updated successfully."
            )

            return redirect(
                "core:subjects"
            )

    else:
        form = SubjectForm(
            instance=subject,
            current_user=request.user,
        )

    context = {
        "form": form,
        "subject": subject,
    }

    return render(
        request,
        "accounts/edit_subject.html",
        context,
    )

@login_required
def teacher_assignments(request):
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

    assignments = TeacherSubject.objects.select_related(
        "teacher",
        "subject",
        "school_class",
        "section",
        "academic_year",
    )

    if not is_product_owner:
        assignments = assignments.filter(
            school_class__tenant=request.user.tenant
        )

    context = {
        "assignments": assignments,
    }

    return render(
        request,
        "accounts/teacher_assignments.html",
        context,
    )


@login_required
def add_teacher_assignment(request):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":
        form = TeacherSubjectForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Teacher assignment created successfully."
            )

            return redirect(
                "core:teacher_assignments"
            )

    else:
        form = TeacherSubjectForm(
            current_user=request.user,
        )

    return render(
        request,
        "accounts/add_teacher_assignment.html",
        {"form": form},
    )


@login_required
def edit_teacher_assignment(request, assignment_id):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    if is_product_owner:
        assignment = get_object_or_404(
            TeacherSubject,
            id=assignment_id,
        )
    else:
        assignment = get_object_or_404(
            TeacherSubject,
            id=assignment_id,
            school_class__tenant=request.user.tenant,
        )

    if request.method == "POST":
        form = TeacherSubjectForm(
            request.POST,
            instance=assignment,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Teacher assignment updated successfully."
            )

            return redirect(
                "core:teacher_assignments"
            )

    else:
        form = TeacherSubjectForm(
            instance=assignment,
            current_user=request.user,
        )

    return render(
        request,
        "accounts/edit_teacher_assignment.html",
        {
            "form": form,
            "assignment": assignment,
        },
    )

@login_required
def add_student(request):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":
        form = StudentForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():
            student = form.save()

            messages.success(
                request,
                "Student created successfully."
            )

            return redirect(
                "core:student_profile",
                student_id=student.id,
            )

    else:
        form = StudentForm(
            current_user=request.user,
        )

    return render(
        request,
        "accounts/add_student.html",
        {"form": form},
    )


@login_required
def edit_student(request, student_id):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    if is_product_owner:
        student = get_object_or_404(
            Student,
            id=student_id,
        )
    else:
        student = get_object_or_404(
            Student,
            id=student_id,
            tenant=request.user.tenant,
        )

    if request.method == "POST":
        form = StudentForm(
            request.POST,
            instance=student,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Student updated successfully."
            )

            return redirect(
                "core:student_profile",
                student_id=student.id,
            )

    else:
        form = StudentForm(
            instance=student,
            current_user=request.user,
        )

    return render(
        request,
        "accounts/edit_student.html",
        {
            "form": form,
            "student": student,
        },
    )


@login_required
def student_profile(request, student_id):
    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    is_school_admin = request.user.groups.filter(
        name="School Admin"
    ).exists()

    is_student = request.user.groups.filter(
        name="Student"
    ).exists()

    if is_product_owner:
        student = get_object_or_404(
            Student,
            id=student_id,
        )

    elif is_school_admin:
        student = get_object_or_404(
            Student,
            id=student_id,
            tenant=request.user.tenant,
        )

    elif is_student:
        student = get_object_or_404(
            Student,
            id=student_id,
            user=request.user,
        )

    else:
        return render(
            request,
            "accounts/access_denied.html",
        )

    return render(
        request,
        "accounts/student_profile.html",
        {"student": student},
    )


@login_required
def toggle_student_status(request, student_id):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    if is_product_owner:
        student = get_object_or_404(
            Student,
            id=student_id,
        )
    else:
        student = get_object_or_404(
            Student,
            id=student_id,
            tenant=request.user.tenant,
        )

    student.is_active = not student.is_active
    student.save()

    if student.is_active:
        messages.success(
            request,
            "Student activated successfully."
        )
    else:
        messages.success(
            request,
            "Student deactivated successfully."
        )

    return redirect(
        "core:students"
    )

@login_required
def add_teacher(request):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":
        form = TeacherForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():
            teacher = form.save()

            messages.success(
                request,
                "Teacher created successfully."
            )

            return redirect(
                "core:teacher_profile",
                teacher_id=teacher.id,
            )

    else:
        form = TeacherForm(
            current_user=request.user,
        )

    return render(
        request,
        "accounts/add_teacher.html",
        {"form": form},
    )


@login_required
def edit_teacher(request, teacher_id):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    if is_product_owner:
        teacher = get_object_or_404(
            Teacher,
            id=teacher_id,
        )
    else:
        teacher = get_object_or_404(
            Teacher,
            id=teacher_id,
            tenant=request.user.tenant,
        )

    if request.method == "POST":
        form = TeacherForm(
            request.POST,
            instance=teacher,
            current_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Teacher updated successfully."
            )

            return redirect(
                "core:teacher_profile",
                teacher_id=teacher.id,
            )

    else:
        form = TeacherForm(
            instance=teacher,
            current_user=request.user,
        )

    return render(
        request,
        "accounts/edit_teacher.html",
        {
            "form": form,
            "teacher": teacher,
        },
    )


@login_required
def teacher_profile(request, teacher_id):
    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    is_school_admin = request.user.groups.filter(
        name="School Admin"
    ).exists()

    is_teacher = request.user.groups.filter(
        name="Teacher"
    ).exists()

    if is_product_owner:
        teacher = get_object_or_404(
            Teacher,
            id=teacher_id,
        )

    elif is_school_admin:
        teacher = get_object_or_404(
            Teacher,
            id=teacher_id,
            tenant=request.user.tenant,
        )

    elif is_teacher:
        teacher = get_object_or_404(
            Teacher,
            id=teacher_id,
            user=request.user,
        )

    else:
        return render(
            request,
            "accounts/access_denied.html",
        )

    assignments = TeacherSubject.objects.filter(
        teacher=teacher
    ).select_related(
        "subject",
        "school_class",
        "section",
        "academic_year",
    )

    return render(
        request,
        "accounts/teacher_profile.html",
        {
            "teacher": teacher,
            "assignments": assignments,
        },
    )


@login_required
def toggle_teacher_status(request, teacher_id):
    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    if is_product_owner:
        teacher = get_object_or_404(
            Teacher,
            id=teacher_id,
        )
    else:
        teacher = get_object_or_404(
            Teacher,
            id=teacher_id,
            tenant=request.user.tenant,
        )

    teacher.is_active = not teacher.is_active
    teacher.save()

    if teacher.is_active:
        messages.success(
            request,
            "Teacher activated successfully."
        )
    else:
        messages.success(
            request,
            "Teacher deactivated successfully."
        )

    return redirect(
        "core:teachers"
    )

@login_required
def record_student_attendance(request):
    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    is_school_admin = request.user.groups.filter(
        name="School Admin"
    ).exists()

    is_teacher = request.user.groups.filter(
        name="Teacher"
    ).exists()

    if not (
        is_product_owner
        or is_school_admin
        or is_teacher
    ):
        return render(
            request,
            "accounts/access_denied.html",
        )

    assignments = TeacherSubject.objects.select_related(
        "teacher",
        "subject",
        "school_class",
        "section",
        "academic_year",
        "school_class__tenant",
    )

    if is_teacher:
        assignments = assignments.filter(
            teacher__user=request.user
        )

    elif is_school_admin:
        assignments = assignments.filter(
            school_class__tenant=request.user.tenant
        )

    assignment_id = request.GET.get(
        "assignment"
    )

    attendance_date = request.GET.get(
        "date"
    )

    selected_assignment = None
    student_list = Student.objects.none()

    if assignment_id:
        try:
            selected_assignment = assignments.get(
                id=assignment_id
            )

            student_list = Student.objects.filter(
                tenant=selected_assignment.school_class.tenant,
                school_class=selected_assignment.school_class,
                section=selected_assignment.section,
                is_active=True,
            ).order_by(
                "first_name",
                "last_name",
            )

        except TeacherSubject.DoesNotExist:
            selected_assignment = None

    if (
        request.method == "POST"
        and selected_assignment
        and attendance_date
    ):
        with transaction.atomic():

            for student in student_list:

                status = request.POST.get(
                    f"status_{student.id}"
                )

                remarks = request.POST.get(
                    f"remarks_{student.id}",
                    ""
                )

                if status:
                    StudentAttendance.objects.update_or_create(
                        student=student,
                        teacher_subject=selected_assignment,
                        attendance_date=attendance_date,
                        defaults={
                            "tenant": selected_assignment.school_class.tenant,
                            "status": status,
                            "remarks": remarks,
                        },
                    )

        messages.success(
            request,
            "Student attendance saved successfully."
        )

        return redirect(
            "core:student_attendance_records"
        )

    context = {
        "assignments": assignments,
        "selected_assignment": selected_assignment,
        "students": student_list,
        "attendance_date": attendance_date,
    }

    return render(
        request,
        "accounts/record_student_attendance.html",
        context,
    )


@login_required
def student_attendance_records(request):
    is_product_owner = request.user.groups.filter(
        name="Product Owner"
    ).exists()

    is_school_admin = request.user.groups.filter(
        name="School Admin"
    ).exists()

    is_teacher = request.user.groups.filter(
        name="Teacher"
    ).exists()

    is_student = request.user.groups.filter(
        name="Student"
    ).exists()

    attendance_list = StudentAttendance.objects.select_related(
        "student",
        "teacher_subject",
        "teacher_subject__teacher",
        "teacher_subject__subject",
        "teacher_subject__school_class",
        "teacher_subject__section",
        "teacher_subject__academic_year",
        "tenant",
    )

    if is_product_owner:
        pass

    elif is_school_admin:
        attendance_list = attendance_list.filter(
            tenant=request.user.tenant
        )

    elif is_teacher:
        attendance_list = attendance_list.filter(
            teacher_subject__teacher__user=request.user
        )

    elif is_student:
        attendance_list = attendance_list.filter(
            student__user=request.user
        )

    else:
        return render(
            request,
            "accounts/access_denied.html",
        )

    attendance_list = attendance_list.order_by(
        "-attendance_date",
        "student__first_name",
    )

    context = {
        "attendance_records": attendance_list,
    }

    return render(
        request,
        "accounts/student_attendance_records.html",
        context,
    )
@login_required
def staff_attendance(request):

    allowed_roles = [
        "School Admin",
        "Teacher",
        "Accountant",
        "Librarian",
    ]

    has_permission = request.user.groups.filter(
        name__in=allowed_roles
    ).exists()

    if not has_permission:
        return render(
            request,
            "accounts/access_denied.html",
        )

    today = timezone.localdate()

    attendance = StaffAttendance.objects.filter(
        user=request.user,
        attendance_date=today,
    ).first()

    if request.method == "POST":

        if attendance is None:

            attendance = StaffAttendance.objects.create(
                tenant=request.user.tenant,
                user=request.user,
                attendance_date=today,
                check_in_time=timezone.localtime().time(),
            )

            messages.success(
                request,
                "Check In recorded successfully."
            )

        elif attendance.check_out_time is None:

            attendance.check_out_time = (
                timezone.localtime().time()
            )

            check_in = datetime.combine(
                today,
                attendance.check_in_time,
            )

            check_out = datetime.combine(
                today,
                attendance.check_out_time,
            )

            total_hours = (
                check_out - check_in
            ).total_seconds() / 3600

            attendance.hours_worked = round(
                total_hours,
                2,
            )

            attendance.save()

            messages.success(
                request,
                "Check Out recorded successfully."
            )

        else:

            messages.info(
                request,
                "Today's attendance has already been completed."
            )

        return redirect(
            "core:staff_attendance"
        )

    context = {
        "attendance": attendance,
        "today": today,
    }

    return render(
        request,
        "accounts/staff_attendance.html",
        context,
    )
@login_required
def staff_attendance_report(request):

    allowed_roles = [
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():
        return render(
            request,
            "accounts/access_denied.html",
        )

    attendance_list = StaffAttendance.objects.select_related(
        "user",
        "tenant",
    ).filter(
        tenant=request.user.tenant,
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:
        attendance_list = attendance_list.filter(
            user__username__icontains=search,
        )

    attendance_list = attendance_list.order_by(
        "-attendance_date",
        "user__username",
    )

    context = {
        "attendance_records": attendance_list,
        "search": search,
    }

    return render(
        request,
        "accounts/staff_attendance_report.html",
        context,
    )
@login_required
def student_timetable(request):

    if not request.user.groups.filter(
        name="Student"
    ).exists():

        return render(
            request,
            "accounts/access_denied.html",
        )

    student = get_object_or_404(
        Student,
        user=request.user,
    )

    timetables = Timetable.objects.select_related(
        "teacher_assignment",
        "teacher_assignment__teacher",
        "teacher_assignment__subject",
        "teacher_assignment__school_class",
        "teacher_assignment__section",
        "academic_term",
    ).filter(
        tenant=request.user.tenant,
        teacher_assignment__school_class=student.school_class,
        teacher_assignment__section=student.section,
    ).order_by(
        "day",
        "start_time",
    )

    context = {
        "student": student,
        "timetables": timetables,
    }

    return render(
        request,
        "core/student_timetable.html",
        context,
    )
@login_required
def teacher_timetable(request):

    if not request.user.groups.filter(
        name="Teacher"
    ).exists():

        return render(
            request,
            "accounts/access_denied.html",
        )

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    timetables = Timetable.objects.select_related(
        "teacher_assignment",
        "teacher_assignment__subject",
        "teacher_assignment__school_class",
        "teacher_assignment__section",
        "academic_term",
    ).filter(
        tenant=request.user.tenant,
        teacher_assignment__teacher=teacher,
    ).order_by(
        "day",
        "start_time",
    )

    context = {

        "teacher": teacher,
        "timetables": timetables,

    }

    return render(
        request,
        "core/teacher_timetable.html",
        context,
    )

@login_required
def timetables(request):

    allowed_roles = [
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

    timetables = Timetable.objects.select_related(
        "teacher_assignment",
        "teacher_assignment__teacher",
        "teacher_assignment__subject",
        "teacher_assignment__school_class",
        "teacher_assignment__section",
        "academic_term",
    )

    if not request.user.groups.filter(
        name="Product Owner"
    ).exists():

        timetables = timetables.filter(
            tenant=request.user.tenant
        )

    search = request.GET.get(
        "search",
        ""
    )

    if search:

        timetables = timetables.filter(

            Q(
                teacher_assignment__teacher__first_name__icontains=search
            )

            |

            Q(
                teacher_assignment__teacher__last_name__icontains=search
            )

            |

            Q(
                teacher_assignment__subject__subject_name__icontains=search
            )

            |

            Q(
                teacher_assignment__school_class__class_name__icontains=search
            )

            |

            Q(
                teacher_assignment__section__section_name__icontains=search
            )

            |

            Q(
                academic_term__term_name__icontains=search
            )

            |

            Q(
                room_number__icontains=search
            )

            |

            Q(
                day__icontains=search
            )

        )

    context = {

        "timetables": timetables.order_by(
            "day",
            "start_time",
        ),

        "search": search,

    }

    return render(
        request,
        "core/timetables.html",
        context,
    )
@login_required
def add_timetable(request):

    if request.method == "POST":

        form = TimetableForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Timetable added successfully."
            )

            return redirect(
                "core:timetables"
            )

    else:

        form = TimetableForm(
            current_user=request.user,
        )

    return render(
        request,
        "core/add_timetable.html",
        {
            "form": form,
        },
    )
@login_required
def edit_timetable(
    request,
    timetable_id,
):

    timetable = get_object_or_404(
        Timetable,
        id=timetable_id,
    )

    if request.user.tenant != timetable.tenant:

        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":

        form = TimetableForm(
            request.POST,
            instance=timetable,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Timetable updated successfully."
            )

            return redirect(
                "core:timetables"
            )

    else:

        form = TimetableForm(
            instance=timetable,
            current_user=request.user,
        )

    return render(
        request,
        "core/edit_timetable.html",
        {
            "form": form,
            "timetable": timetable,
        },
    )
@login_required
def delete_timetable(
    request,
    timetable_id,
):

    timetable = get_object_or_404(
        Timetable,
        id=timetable_id,
    )

    if request.user.tenant != timetable.tenant:

        return render(
            request,
            "accounts/access_denied.html",
        )

    timetable.delete()

    messages.success(
        request,
        "Timetable deleted successfully."
    )

    return redirect(
        "core:timetables"
    )
@login_required
def examinations(request):

    allowed_roles = [
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():

        return render(
            request,
            "accounts/access_denied.html",
        )

    examinations = Examination.objects.select_related(
        "academic_term",
        "school_class",
        "subject",
    )

    if not request.user.groups.filter(
        name="Product Owner"
    ).exists():

        examinations = examinations.filter(
            tenant=request.user.tenant
        )

    search = request.GET.get(
        "search",
        ""
    )

    if search:

        examinations = examinations.filter(

            Q(subject__subject_name__icontains=search)

            |

            Q(school_class__class_name__icontains=search)

            |

            Q(exam_type__icontains=search)

            |

            Q(academic_term__term_name__icontains=search)

        )

    context = {

        "examinations": examinations,

        "search": search,

    }

    return render(
        request,
        "core/examinations.html",
        context,
    )
@login_required
def add_examination(request):

    if request.method == "POST":

        form = ExaminationForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Examination created successfully."
            )

            return redirect(
                "core:examinations"
            )

    else:

        form = ExaminationForm(
            current_user=request.user,
        )

    return render(
        request,
        "core/add_examination.html",
        {
            "form": form,
        },
    )
@login_required
def edit_examination(
    request,
    examination_id,
):

    examination = get_object_or_404(
        Examination,
        id=examination_id,
    )

    if (
        request.user.tenant != examination.tenant
        and not request.user.groups.filter(
            name="Product Owner"
        ).exists()
    ):

        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":

        form = ExaminationForm(
            request.POST,
            instance=examination,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Examination updated successfully."
            )

            return redirect(
                "core:examinations"
            )

    else:

        form = ExaminationForm(
            instance=examination,
            current_user=request.user,
        )

    return render(
        request,
        "core/edit_examination.html",
        {
            "form": form,
            "examination": examination,
        },
    )
@login_required
def delete_examination(
    request,
    examination_id,
):

    examination = get_object_or_404(
        Examination,
        id=examination_id,
    )

    if (
        request.user.tenant != examination.tenant
        and not request.user.groups.filter(
            name="Product Owner"
        ).exists()
    ):

        return render(
            request,
            "accounts/access_denied.html",
        )

    examination.delete()

    messages.success(
        request,
        "Examination deleted successfully."
    )

    return redirect(
        "core:examinations"
    )
@login_required
def toggle_exam_publish(
    request,
    examination_id,
):

    examination = get_object_or_404(
        Examination,
        id=examination_id,
    )

    if (
        request.user.tenant != examination.tenant
        and not request.user.groups.filter(
            name="Product Owner"
        ).exists()
    ):

        return render(
            request,
            "accounts/access_denied.html",
        )

    examination.is_published = (
        not examination.is_published
    )

    examination.save()

    if examination.is_published:

        messages.success(
            request,
            "Examination published successfully."
        )

    else:

        messages.success(
            request,
            "Examination unpublished successfully."
        )

    return redirect(
        "core:examinations"
    )
@login_required
def exam_hall_allocations(request):

    allowed_roles = [
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():

        return render(
            request,
            "accounts/access_denied.html",
        )

    allocations = ExamHallAllocation.objects.select_related(
        "examination",
        "section",
        "invigilator",
        "examination__subject",
        "examination__school_class",
    )

    if not request.user.groups.filter(
        name="Product Owner"
    ).exists():

        allocations = allocations.filter(
            tenant=request.user.tenant
        )

    search = request.GET.get(
        "search",
        ""
    )

    if search:

        allocations = allocations.filter(

            Q(
                examination__subject__subject_name__icontains=search
            )

            |

            Q(
                examination__school_class__class_name__icontains=search
            )

            |

            Q(
                section__section_name__icontains=search
            )

            |

            Q(
                hall_name__icontains=search
            )

            |

            Q(
                invigilator__first_name__icontains=search
            )

            |

            Q(
                invigilator__last_name__icontains=search
            )

        )

    context = {

        "allocations": allocations,

        "search": search,

    }

    return render(
        request,
        "core/exam_hall_allocations.html",
        context,
    )
@login_required
def manage_exam_halls(
    request,
    examination_id,
):

    examination = get_object_or_404(
        Examination,
        id=examination_id,
    )

    if (
        request.user.tenant != examination.tenant
        and not request.user.groups.filter(
            name="Product Owner"
        ).exists()
    ):
        return render(
            request,
            "accounts/access_denied.html",
        )

    allocations = (
        ExamHallAllocation.objects.select_related(
            "section",
            "invigilator",
        )
        .filter(
            examination=examination
        )
        .order_by(
            "section__section_name"
        )
    )

    return render(
        request,
        "core/manage_exam_halls.html",
        {
            "examination": examination,
            "allocations": allocations,
        },
    )


@login_required
def add_exam_hall(
    request,
    examination_id,
):

    examination = get_object_or_404(
        Examination,
        id=examination_id,
    )

    if (
        request.user.tenant != examination.tenant
        and not request.user.groups.filter(
            name="Product Owner"
        ).exists()
    ):
        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":

        form = ExamHallAllocationForm(
            request.POST,
            current_user=request.user,
            examination=examination,
        )

        form.fields["section"].queryset = (
            Section.objects.filter(
                school_class=examination.school_class
            )
        )

        if form.is_valid():

            allocation = form.save(
                commit=False
            )

            allocation.examination = examination
            allocation.tenant = examination.tenant

            allocation.save()

            messages.success(
                request,
                "Hall allocation created successfully."
            )

            return redirect(
                "core:manage_exam_halls",
                examination.id,
            )

    else:

        form = ExamHallAllocationForm(
            current_user=request.user,
            examination=examination,
        )

        form.fields["section"].queryset = (
            Section.objects.filter(
                school_class=examination.school_class
            )
        )

    return render(
        request,
        "core/add_exam_hall.html",
        {
            "form": form,
            "examination": examination,
        },
    )


@login_required
def edit_exam_hall(
    request,
    allocation_id,
):

    allocation = get_object_or_404(
        ExamHallAllocation,
        id=allocation_id,
    )

    if (
        request.user.tenant != allocation.tenant
        and not request.user.groups.filter(
            name="Product Owner"
        ).exists()
    ):
        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":

        form = ExamHallAllocationForm(
            request.POST,
            instance=allocation,
            current_user=request.user,
            examination=allocation.examination,
        )

        form.fields["section"].queryset = (
            Section.objects.filter(
                school_class=allocation.examination.school_class
            )
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Hall allocation updated successfully."
            )

            return redirect(
                "core:manage_exam_halls",
                allocation.examination.id,
            )

    else:

        form = ExamHallAllocationForm(
            instance=allocation,
            current_user=request.user,
            examination=allocation.examination,
        )

        form.fields["section"].queryset = (
            Section.objects.filter(
                school_class=allocation.examination.school_class
            )
        )

    return render(
        request,
        "core/edit_exam_hall.html",
        {
            "form": form,
            "allocation": allocation,
        },
    )


@login_required
def delete_exam_hall(
    request,
    allocation_id,
):

    allocation = get_object_or_404(
        ExamHallAllocation,
        id=allocation_id,
    )

    if (
        request.user.tenant != allocation.tenant
        and not request.user.groups.filter(
            name="Product Owner"
        ).exists()
    ):
        return render(
            request,
            "accounts/access_denied.html",
        )

    examination_id = allocation.examination.id

    allocation.delete()

    messages.success(
        request,
        "Hall allocation deleted successfully."
    )

    return redirect(
        "core:manage_exam_halls",
        examination_id,
    )
@login_required
def teacher_invigilation(request):
    if not request.user.groups.filter(
        name="Teacher"
    ).exists():

        return render(
            request,
            "accounts/access_denied.html",
        )

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    invigilations = (
        ExamHallAllocation.objects
        .select_related(
            "examination",
            "section",
        )
        .filter(
            invigilator=teacher
        )
        .order_by(
            "examination__exam_date",
            "examination__start_time",
        )
    )

    return render(
        request,
        "core/teacher_invigilation.html",
        {
            "invigilations": invigilations,
        },
    )
@login_required
def student_examinations(request):

    if not request.user.groups.filter(
        name="Student"
    ).exists():

        return render(
            request,
            "accounts/access_denied.html",
        )

    student = get_object_or_404(
        Student,
        user=request.user,
    )

    examinations = (
        ExamHallAllocation.objects
        .select_related(
            "examination",
            "section",
        )
        .filter(
            section=student.section,
        )
        .order_by(
            "examination__exam_date",
            "examination__start_time",
        )
    )

    return render(
        request,
        "core/student_examinations.html",
        {
            "student": student,
            "examinations": examinations,
        },
    )
@login_required
def teacher_marks(request):

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    teacher_assignments = TeacherSubject.objects.filter(
        teacher=teacher
    ).select_related(
        "school_class",
        "section",
        "subject",
        "academic_year",
    )

    return render(
        request,
        "core/teacher_marks.html",
        {
            "teacher_assignments": teacher_assignments,
        },
    )


@login_required
def enter_marks(
    request,
    assignment_id,
    examination_id,
):

    assignment = get_object_or_404(
        TeacherSubject,
        id=assignment_id,
    )

    examination = get_object_or_404(
        Examination,
        id=examination_id,
    )

    students = Student.objects.filter(
        school_class=assignment.school_class,
        section=assignment.section,
        is_active=True,
    ).order_by(
        "first_name",
        "last_name",
    )

    student_rows = []

    for student in students:

        mark = StudentMark.objects.filter(
            examination=examination,
            student=student,
        ).first()

        student_rows.append({

            "student": student,

            "mark": mark,

        })

    if request.method == "POST":

        for student in students:

            marks = request.POST.get(
                f"marks_{student.id}"
            )

            remarks = request.POST.get(
                f"remarks_{student.id}"
            )

            if not marks:
                continue

            StudentMark.objects.update_or_create(

                examination=examination,

                student=student,

                defaults={

                    "tenant": assignment.teacher.tenant,

                    "marks_obtained": marks,

                    "remarks": remarks,

                    "entered_by": assignment.teacher,

                },

            )

        messages.success(
            request,
            "Student marks saved successfully."
        )

        return redirect(
            "core:assignment_examinations",
            assignment.id,
        )

    context = {

        "assignment": assignment,

        "examination": examination,

        "student_rows": student_rows,

    }

    return render(

        request,

        "core/enter_marks.html",

        context,

    )
@login_required
def assignment_examinations(
    request,
    assignment_id,
):

    assignment = get_object_or_404(
        TeacherSubject,
        id=assignment_id,
    )

    examinations = Examination.objects.filter(
        school_class=assignment.school_class,
        subject=assignment.subject,
        academic_term__academic_year=assignment.academic_year,
    ).order_by(
        "exam_date",
    )

    context = {

        "assignment": assignment,

        "examinations": examinations,

    }

    return render(
        request,
        "core/assignment_examinations.html",
        context,
    )
@login_required
def results(request):

    allowed_roles = [
        "Product Owner",
        "School Admin",
    ]

    if not request.user.groups.filter(
        name__in=allowed_roles
    ).exists():

        return render(
            request,
            "accounts/access_denied.html",
        )

    result_list = Result.objects.select_related(
        "student",
        "academic_term",
    )

    if not request.user.groups.filter(
        name="Product Owner"
    ).exists():

        result_list = result_list.filter(
            tenant=request.user.tenant
        )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        result_list = result_list.filter(

            Q(student__student_id__icontains=search)

            |

            Q(student__first_name__icontains=search)

            |

            Q(student__last_name__icontains=search)

        )

    context = {

        "results": result_list.order_by(
            "student__first_name",
        ),

        "search": search,

        "academic_terms": AcademicTerm.objects.filter(
            academic_year__tenant=request.user.tenant
        ),

    }

    return render(
        request,
        "core/results.html",
        context,
    )


@login_required
def generate_results(
    request,
    academic_term_id,
):

    academic_term = get_object_or_404(
        AcademicTerm,
        id=academic_term_id,
    )

    students = Student.objects.filter(
        tenant=request.user.tenant,
        is_active=True,
    )

    generated = 0

    for student in students:

        marks = StudentMark.objects.filter(
            student=student,
            examination__academic_term=academic_term,
        ).select_related(
            "examination",
        )

        if not marks.exists():
            continue

        total_obtained = 0
        total_maximum = 0
        passed = True

        for mark in marks:

            total_obtained += float(
                mark.marks_obtained
            )

            total_maximum += float(
                mark.examination.total_marks
            )

            if (
                mark.marks_obtained
                <
                mark.examination.passing_marks
            ):
                passed = False

        percentage = (
            total_obtained
            /
            total_maximum
        ) * 100

        if percentage >= 90:
            grade = "A+"

        elif percentage >= 80:
            grade = "A"

        elif percentage >= 70:
            grade = "B"

        elif percentage >= 60:
            grade = "C"

        elif percentage >= 50:
            grade = "D"

        else:
            grade = "F"

        Result.objects.update_or_create(

            tenant=request.user.tenant,

            student=student,

            academic_term=academic_term,

            defaults={

                "total_marks": total_obtained,

                "percentage": round(
                    percentage,
                    2,
                ),

                "grade": grade,

                "result_status": (
                    "PASS"
                    if passed
                    else "FAIL"
                ),

                "is_published": False,

            }

        )

        generated += 1

    messages.success(

        request,

        f"{generated} result(s) generated successfully."

    )

    return redirect(
        "core:results"
    )


@login_required
def toggle_result_publish(
    request,
    result_id,
):

    result = get_object_or_404(
        Result,
        id=result_id,
    )

    if result.tenant != request.user.tenant:

        return render(
            request,
            "accounts/access_denied.html",
        )

    result.is_published = (
        not result.is_published
    )

    result.save()

    if result.is_published:

        messages.success(
            request,
            "Result published successfully."
        )

    else:

        messages.success(
            request,
            "Result unpublished successfully."
        )

    return redirect(
        "core:results"
    )
@login_required
def teacher_results(request):

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    assignments = TeacherSubject.objects.filter(
        teacher=teacher,
    )

    results = Result.objects.filter(
        tenant=request.user.tenant,
        is_published=True,
    ).select_related(
        "student",
        "academic_term",
    )

    return render(

        request,

        "core/teacher_results.html",

        {

            "results": results,

            "assignments": assignments,

        },

    )
@login_required
def student_results(request):

    student = get_object_or_404(
        Student,
        user=request.user,
    )

    results = Result.objects.filter(

        student=student,

        is_published=True,

    )

    return render(

        request,

        "core/student_results.html",

        {

            "results": results,

        },

    )
@login_required
def result_details(
    request,
    result_id,
):

    result = get_object_or_404(
        Result,
        id=result_id,
    )

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

    # -----------------------------
    # Permission Check
    # -----------------------------

    if is_product_owner:

        pass

    elif is_school_admin:

        if result.tenant != user.tenant:
            return render(
                request,
                "accounts/access_denied.html",
            )

    elif is_teacher:

        teacher = get_object_or_404(
            Teacher,
            user=user,
        )

        teaches_student = TeacherSubject.objects.filter(
            teacher=teacher,
            school_class=result.student.school_class,
            section=result.student.section,
        ).exists()

        if not teaches_student:
            return render(
                request,
                "accounts/access_denied.html",
            )

    elif is_student:

        student = get_object_or_404(
            Student,
            user=user,
        )

        if student != result.student:
            return render(
                request,
                "accounts/access_denied.html",
            )

    else:

        return render(
            request,
            "accounts/access_denied.html",
        )

    # -----------------------------
    # Subject Wise Marks
    # -----------------------------

    marks = (
        StudentMark.objects
        .filter(
            student=result.student,
            examination__academic_term=result.academic_term,
        )
        .select_related(
            "examination",
            "examination__subject",
        )
        .order_by(
            "examination__subject__subject_name",
        )
    )

    context = {

        "result": result,

        "student": result.student,

        "marks": marks,

        "academic_year": result.academic_term.academic_year,

        "school_class": result.student.school_class,

        "section": result.student.section,

    }

    return render(
        request,
        "core/report_card.html",
        context,
    )
@login_required
def print_report_card(
    request,
    result_id,
):

    result = get_object_or_404(
        Result,
        id=result_id,
    )

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

    if is_product_owner:

        pass

    elif is_school_admin:

        if result.tenant != user.tenant:

            return render(
                request,
                "accounts/access_denied.html",
            )

    elif is_teacher:

        teacher = get_object_or_404(
            Teacher,
            user=user,
        )

        teaches_student = TeacherSubject.objects.filter(
            teacher=teacher,
            school_class=result.student.school_class,
            section=result.student.section,
        ).exists()

        if not teaches_student:

            return render(
                request,
                "accounts/access_denied.html",
            )

    elif is_student:

        student = get_object_or_404(
            Student,
            user=user,
        )

        if student != result.student:

            return render(
                request,
                "accounts/access_denied.html",
            )

    else:

        return render(
            request,
            "accounts/access_denied.html",
        )

    marks = StudentMark.objects.filter(
        student=result.student,
        examination__academic_term=result.academic_term,
    ).select_related(
        "examination",
        "examination__subject",
    ).order_by(
        "examination__subject__subject_name",
    )

    context = {

        "result": result,

        "student": result.student,

        "marks": marks,

        "academic_year": result.academic_term.academic_year,

        "school_class": result.student.school_class,

        "section": result.student.section,

    }

    return render(
        request,
        "core/report_card_print.html",
        context,
    )
def can_manage_fees(user):
    return (
        user.groups.filter(name="School Admin").exists()
        or user.groups.filter(name="Accountant").exists()
    )


def get_fee_tenant_filter(user):
    if user.groups.filter(name="Product Owner").exists():
        return {}

    return {
        "tenant": user.tenant
    }


@login_required
def fee_structures(request):

    if not can_manage_fees(request.user):
        return render(request, "accounts/access_denied.html")

    search_query = request.GET.get("q", "")

    fee_structures = FeeStructure.objects.select_related(
        "tenant",
        "academic_term",
        "school_class",
    )

    if not request.user.groups.filter(name="Product Owner").exists():
        fee_structures = fee_structures.filter(
            tenant=request.user.tenant
        )

    if search_query:
        fee_structures = fee_structures.filter(
            Q(fee_name__icontains=search_query)
            | Q(school_class__class_name__icontains=search_query)
            | Q(academic_term__term_name__icontains=search_query)
        )

    context = {
        "fee_structures": fee_structures,
        "search_query": search_query,
    }

    return render(
        request,
        "core/fee_structures.html",
        context,
    )


@login_required
def add_fee_structure(request):

    if not can_manage_fees(request.user):
        return render(request, "accounts/access_denied.html")

    if request.method == "POST":

        form = FeeStructureForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Fee structure created successfully.",
            )

            return redirect(
                "core:fee_structures"
            )

    else:

        form = FeeStructureForm(
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Add Fee Structure",
    }

    return render(
        request,
        "core/fee_structure_form.html",
        context,
    )


@login_required
def edit_fee_structure(request, fee_structure_id):

    if not can_manage_fees(request.user):
        return render(request, "accounts/access_denied.html")

    fee_structure = get_object_or_404(
        FeeStructure,
        id=fee_structure_id,
    )

    if (
        not request.user.groups.filter(name="Product Owner").exists()
        and fee_structure.tenant != request.user.tenant
    ):
        return render(request, "accounts/access_denied.html")

    if request.method == "POST":

        form = FeeStructureForm(
            request.POST,
            instance=fee_structure,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Fee structure updated successfully.",
            )

            return redirect(
                "core:fee_structures"
            )

    else:

        form = FeeStructureForm(
            instance=fee_structure,
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Edit Fee Structure",
    }

    return render(
        request,
        "core/fee_structure_form.html",
        context,
    )


@login_required
def student_fees(request):

    if not can_manage_fees(request.user):
        return render(request, "accounts/access_denied.html")

    search_query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")

    student_fees = StudentFee.objects.select_related(
        "tenant",
        "student",
        "fee_structure",
        "fee_structure__academic_term",
        "fee_structure__school_class",
    )

    if not request.user.groups.filter(name="Product Owner").exists():
        student_fees = student_fees.filter(
            tenant=request.user.tenant
        )

    if search_query:
        student_fees = student_fees.filter(
            Q(student__student_id__icontains=search_query)
            | Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
            | Q(fee_structure__fee_name__icontains=search_query)
        )

    if status_filter:
        student_fees = student_fees.filter(
            status=status_filter
        )

    context = {
        "student_fees": student_fees,
        "search_query": search_query,
        "status_filter": status_filter,
    }

    return render(
        request,
        "core/student_fees.html",
        context,
    )


@login_required
def assign_student_fee(request):

    if not can_manage_fees(request.user):
        return render(request, "accounts/access_denied.html")

    if request.method == "POST":

        form = StudentFeeForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Fee assigned to student successfully.",
            )

            return redirect(
                "core:student_fees"
            )

    else:

        form = StudentFeeForm(
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Assign Fee to Student",
    }

    return render(
        request,
        "core/student_fee_form.html",
        context,
    )


@login_required
def collect_fee_payment(request, student_fee_id):

    if not can_manage_fees(request.user):
        return render(request, "accounts/access_denied.html")

    student_fee = get_object_or_404(
        StudentFee.objects.select_related(
            "student",
            "fee_structure",
            "tenant",
        ),
        id=student_fee_id,
    )

    if (
        not request.user.groups.filter(name="Product Owner").exists()
        and student_fee.tenant != request.user.tenant
    ):
        return render(request, "accounts/access_denied.html")

    if student_fee.status == "Paid":

        messages.info(
            request,
            "This fee is already fully paid.",
        )

        return redirect(
            "core:student_fees"
        )

    if request.method == "POST":

        post_data = request.POST.copy()
        post_data["student_fee"] = student_fee.id

        form = FeePaymentForm(
            post_data,
            current_user=request.user,
        )

        form.fields["student_fee"].widget = forms.HiddenInput()

        if form.is_valid():

            with transaction.atomic():

                payment = form.save()

                student_fee.paid_amount = (
                    student_fee.paid_amount
                    + payment.amount_paid
                )

                student_fee.save()

            messages.success(
                request,
                "Payment collected successfully.",
            )

            return redirect(
                "core:student_fees"
            )

    else:

        form = FeePaymentForm(
            initial={
                "student_fee": student_fee,
                "payment_date": timezone.localdate(),
            },
            current_user=request.user,
        )

        form.fields["student_fee"].widget = forms.HiddenInput()

    context = {
        "form": form,
        "student_fee": student_fee,
        "title": "Collect Fee Payment",
    }

    return render(
        request,
        "core/collect_fee_payment.html",
        context,
    )


@login_required
def fee_payments(request):

    if not can_manage_fees(request.user):
        return render(request, "accounts/access_denied.html")

    search_query = request.GET.get("q", "")

    payments = FeePayment.objects.select_related(
        "student_fee",
        "student_fee__student",
        "student_fee__fee_structure",
        "recorded_by",
    )

    if not request.user.groups.filter(name="Product Owner").exists():
        payments = payments.filter(
            student_fee__tenant=request.user.tenant
        )

    if search_query:
        payments = payments.filter(
            Q(student_fee__student__student_id__icontains=search_query)
            | Q(student_fee__student__first_name__icontains=search_query)
            | Q(student_fee__student__last_name__icontains=search_query)
            | Q(student_fee__fee_structure__fee_name__icontains=search_query)
            | Q(reference_number__icontains=search_query)
        )

    context = {
        "payments": payments,
        "search_query": search_query,
    }

    return render(
        request,
        "core/fee_payments.html",
        context,
    )
@login_required
def bulk_assign_student_fee(request):

    if not can_manage_fees(request.user):
        return render(request, "accounts/access_denied.html")

    if request.method == "POST":

        form = BulkStudentFeeAssignForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            fee_structure = form.cleaned_data["fee_structure"]
            section = form.cleaned_data.get("section")

            if (
                not request.user.groups.filter(name="Product Owner").exists()
                and fee_structure.tenant != request.user.tenant
            ):
                return render(request, "accounts/access_denied.html")

            students = Student.objects.filter(
                tenant=fee_structure.tenant,
                school_class=fee_structure.school_class,
                is_active=True,
            )

            if section:
                students = students.filter(
                    section=section
                )

            assigned_count = 0
            skipped_count = 0

            with transaction.atomic():

                for student in students:

                    student_fee, created = StudentFee.objects.get_or_create(
                        student=student,
                        fee_structure=fee_structure,
                        defaults={
                            "tenant": student.tenant,
                            "total_amount": fee_structure.amount,
                            "paid_amount": 0,
                        },
                    )

                    if created:
                        assigned_count = assigned_count + 1
                    else:
                        skipped_count = skipped_count + 1

            messages.success(
                request,
                f"Bulk fee assignment completed. Assigned: {assigned_count}, Already existed: {skipped_count}.",
            )

            return redirect(
                "core:student_fees"
            )

    else:

        form = BulkStudentFeeAssignForm(
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Bulk Assign Fee",
    }

    return render(
        request,
        "core/bulk_assign_student_fee.html",
        context,
    )
@login_required
def my_fees(request):

    if not request.user.groups.filter(name="Student").exists():
        return render(request, "accounts/access_denied.html")

    student = get_object_or_404(
        Student,
        user=request.user,
    )

    student_fees = StudentFee.objects.filter(
        student=student,
    ).select_related(
        "fee_structure",
        "fee_structure__academic_term",
        "fee_structure__school_class",
    )

    payments = FeePayment.objects.filter(
        student_fee__student=student,
    ).select_related(
        "student_fee",
        "student_fee__fee_structure",
    )

    context = {
        "student": student,
        "student_fees": student_fees,
        "payments": payments,
    }

    return render(
        request,
        "core/my_fees.html",
        context,
    )
def can_manage_library(user):
    return (
        user.groups.filter(name="School Admin").exists()
        or user.groups.filter(name="Librarian").exists()
    )


@login_required
def book_categories(request):

    if not can_manage_library(request.user):
        return render(request, "accounts/access_denied.html")

    search_query = request.GET.get("q", "")

    categories = BookCategory.objects.all()

    if not request.user.groups.filter(name="Product Owner").exists():
        categories = categories.filter(
            tenant=request.user.tenant
        )

    if search_query:
        categories = categories.filter(
            Q(category_name__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    context = {
        "categories": categories,
        "search_query": search_query,
    }

    return render(
        request,
        "core/book_categories.html",
        context,
    )


@login_required
def add_book_category(request):

    if not can_manage_library(request.user):
        return render(request, "accounts/access_denied.html")

    if request.method == "POST":

        form = BookCategoryForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Book category added successfully.",
            )

            return redirect(
                "core:book_categories"
            )

    else:

        form = BookCategoryForm(
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Add Book Category",
    }

    return render(
        request,
        "core/book_category_form.html",
        context,
    )


@login_required
def edit_book_category(request, category_id):

    if not can_manage_library(request.user):
        return render(request, "accounts/access_denied.html")

    category = get_object_or_404(
        BookCategory,
        id=category_id,
    )

    if (
        not request.user.groups.filter(name="Product Owner").exists()
        and category.tenant != request.user.tenant
    ):
        return render(request, "accounts/access_denied.html")

    if request.method == "POST":

        form = BookCategoryForm(
            request.POST,
            instance=category,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Book category updated successfully.",
            )

            return redirect(
                "core:book_categories"
            )

    else:

        form = BookCategoryForm(
            instance=category,
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Edit Book Category",
    }

    return render(
        request,
        "core/book_category_form.html",
        context,
    )


@login_required
def books(request):

    if not can_manage_library(request.user):
        return render(request, "accounts/access_denied.html")

    search_query = request.GET.get("q", "")
    category_filter = request.GET.get("category", "")

    books = Book.objects.select_related(
        "tenant",
        "category",
    )

    if not request.user.groups.filter(name="Product Owner").exists():
        books = books.filter(
            tenant=request.user.tenant
        )

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query)
            | Q(author__icontains=search_query)
            | Q(isbn__icontains=search_query)
            | Q(publisher__icontains=search_query)
        )

    if category_filter:
        books = books.filter(
            category_id=category_filter
        )

    categories = BookCategory.objects.filter(
        is_active=True
    )

    if not request.user.groups.filter(name="Product Owner").exists():
        categories = categories.filter(
            tenant=request.user.tenant
        )

    context = {
        "books": books,
        "categories": categories,
        "search_query": search_query,
        "category_filter": category_filter,
    }

    return render(
        request,
        "core/books.html",
        context,
    )


@login_required
def add_book(request):

    if not can_manage_library(request.user):
        return render(request, "accounts/access_denied.html")

    if request.method == "POST":

        form = BookForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Book added successfully.",
            )

            return redirect(
                "core:books"
            )

    else:

        form = BookForm(
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Add Book",
    }

    return render(
        request,
        "core/book_form.html",
        context,
    )


@login_required
def edit_book(request, book_id):

    if not can_manage_library(request.user):
        return render(request, "accounts/access_denied.html")

    book = get_object_or_404(
        Book,
        id=book_id,
    )

    if (
        not request.user.groups.filter(name="Product Owner").exists()
        and book.tenant != request.user.tenant
    ):
        return render(request, "accounts/access_denied.html")

    if request.method == "POST":

        form = BookForm(
            request.POST,
            instance=book,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Book updated successfully.",
            )

            return redirect(
                "core:books"
            )

    else:

        form = BookForm(
            instance=book,
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Edit Book",
    }

    return render(
        request,
        "core/book_form.html",
        context,
    )


@login_required
def library_issues(request):

    if not can_manage_library(request.user):
        return render(request, "accounts/access_denied.html")

    search_query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")

    issues = LibraryIssue.objects.select_related(
        "tenant",
        "book",
        "student",
        "teacher",
        "issued_by",
        "returned_by",
    )

    if not request.user.groups.filter(name="Product Owner").exists():
        issues = issues.filter(
            tenant=request.user.tenant
        )

    if search_query:
        issues = issues.filter(
            Q(book__title__icontains=search_query)
            | Q(book__author__icontains=search_query)
            | Q(student__student_id__icontains=search_query)
            | Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
            | Q(teacher__teacher_id__icontains=search_query)
            | Q(teacher__first_name__icontains=search_query)
            | Q(teacher__last_name__icontains=search_query)
        )

    if status_filter:
        issues = issues.filter(
            status=status_filter
        )

    context = {
        "issues": issues,
        "search_query": search_query,
        "status_filter": status_filter,
    }

    return render(
        request,
        "core/library_issues.html",
        context,
    )


@login_required
def issue_book(request):

    if not can_manage_library(request.user):
        return render(request, "accounts/access_denied.html")

    selected_book_id = request.GET.get("book")

    if request.method == "POST":

        form = LibraryIssueForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            with transaction.atomic():

                issue = form.save(
                    commit=False
                )

                book = Book.objects.select_for_update().get(
                    id=issue.book.id
                )

                if book.available_copies <= 0:

                    messages.error(
                        request,
                        "This book is not available right now.",
                    )

                    return redirect(
                        "core:books"
                    )

                duplicate_issue = LibraryIssue.objects.filter(
                    book=book,
                    status="Borrowed",
                )

                if issue.member_type == "Student":

                    duplicate_issue = duplicate_issue.filter(
                        student=issue.student
                    )

                elif issue.member_type == "Teacher":

                    duplicate_issue = duplicate_issue.filter(
                        teacher=issue.teacher
                    )

                if duplicate_issue.exists():

                    messages.warning(
                        request,
                        "This member has already borrowed this book and has not returned it yet.",
                    )

                    return redirect(
                        "core:library_issues"
                    )

                issue.book = book
                issue.tenant = book.tenant
                issue.status = "Borrowed"
                issue.issued_by = request.user

                book.available_copies = book.available_copies - 1
                book.save()

                issue.save()

            messages.success(
                request,
                "Book issued successfully.",
            )

            return redirect(
                "core:library_issues"
            )

    else:

        initial_data = {
            "issue_date": timezone.localdate(),
            "due_date": timezone.localdate() + timezone.timedelta(days=14),
        }

        if selected_book_id:
            initial_data["book"] = selected_book_id

        form = LibraryIssueForm(
            initial=initial_data,
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Issue Book",
    }

    return render(
        request,
        "core/issue_book.html",
        context,
    )


@login_required
def return_book(request, issue_id):

    if not can_manage_library(request.user):
        return render(request, "accounts/access_denied.html")

    issue = get_object_or_404(
        LibraryIssue.objects.select_related(
            "tenant",
            "book",
            "student",
            "teacher",
        ),
        id=issue_id,
    )

    if (
        not request.user.groups.filter(name="Product Owner").exists()
        and issue.tenant != request.user.tenant
    ):
        return render(request, "accounts/access_denied.html")

    if issue.status != "Borrowed":

        messages.info(
            request,
            "This book has already been returned or closed.",
        )

        return redirect(
            "core:library_issues"
        )

    today = timezone.localdate()
    suggested_fine = Decimal("0.00")

    if today > issue.due_date:
        late_days = (today - issue.due_date).days
        suggested_fine = Decimal(late_days) * Decimal("1.00")

    if request.method == "POST":

        form = ReturnBookForm(
            request.POST,
            instance=issue,
        )

        if form.is_valid():

            with transaction.atomic():

                locked_issue = LibraryIssue.objects.select_for_update().select_related(
                    "book"
                ).get(
                    id=issue.id
                )

                book = Book.objects.select_for_update().get(
                    id=locked_issue.book.id
                )

                locked_issue.return_date = form.cleaned_data["return_date"]
                locked_issue.fine_amount = form.cleaned_data["fine_amount"]
                locked_issue.remarks = form.cleaned_data["remarks"]
                locked_issue.status = "Returned"
                locked_issue.returned_by = request.user
                locked_issue.save()

                if book.available_copies < book.total_copies:
                    book.available_copies = book.available_copies + 1
                    book.save()

            messages.success(
                request,
                "Book returned successfully.",
            )

            return redirect(
                "core:library_issues"
            )

    else:

        form = ReturnBookForm(
            instance=issue,
            initial={
                "return_date": today,
                "fine_amount": suggested_fine,
            },
        )

    context = {
        "form": form,
        "issue": issue,
        "title": "Return Book",
    }

    return render(
        request,
        "core/return_book.html",
        context,
    )


@login_required
def my_library_records(request):

    is_student = request.user.groups.filter(
        name="Student"
    ).exists()

    is_teacher = request.user.groups.filter(
        name="Teacher"
    ).exists()

    if not is_student and not is_teacher:
        return render(request, "accounts/access_denied.html")

    if is_student:

        student = get_object_or_404(
            Student,
            user=request.user,
        )

        issues = LibraryIssue.objects.filter(
            student=student,
        ).select_related(
            "book",
            "tenant",
        )

        member_name = f"{student.first_name} {student.last_name}"

    else:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
        )

        issues = LibraryIssue.objects.filter(
            teacher=teacher,
        ).select_related(
            "book",
            "tenant",
        )

        member_name = f"{teacher.first_name} {teacher.last_name}"

    context = {
        "issues": issues,
        "member_name": member_name,
    }

    return render(
        request,
        "core/my_library_records.html",
        context,
    )
def can_view_reports(user):

    return (
        user.groups.filter(name="School Admin").exists()
        or user.groups.filter(name="Accountant").exists()
        or user.groups.filter(name="Librarian").exists()
    )


def is_product_owner(user):

    return user.groups.filter(
        name="Product Owner"
    ).exists()


def is_school_admin(user):

    return user.groups.filter(
        name="School Admin"
    ).exists()


def is_accountant(user):

    return user.groups.filter(
        name="Accountant"
    ).exists()


def is_librarian(user):

    return user.groups.filter(
        name="Librarian"
    ).exists()


def get_current_user_tenant(user):

    if is_product_owner(user):
        return None

    return user.tenant


@login_required
def reports_dashboard(request):

    if not can_view_reports(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    tenant = get_current_user_tenant(
        request.user
    )

    show_academic_reports = (
        is_school_admin(request.user)
    )

    show_fee_reports = (
        is_school_admin(request.user)
        or is_accountant(request.user)
    )

    show_library_reports = (
        is_school_admin(request.user)
        or is_librarian(request.user)
    )

    show_exam_reports = (
            is_school_admin(request.user)
    )

    students = Student.objects.all()
    teachers = Teacher.objects.all()
    classes = SchoolClass.objects.all()
    subjects = Subject.objects.all()
    examinations = Examination.objects.all()
    results = Result.objects.all()
    student_fees = StudentFee.objects.all()
    fee_payments = FeePayment.objects.all()
    books = Book.objects.all()
    library_issues = LibraryIssue.objects.all()

    if tenant is not None:

        students = students.filter(
            tenant=tenant
        )

        teachers = teachers.filter(
            tenant=tenant
        )

        classes = classes.filter(
            tenant=tenant
        )

        subjects = subjects.filter(
            tenant=tenant
        )

        examinations = examinations.filter(
            tenant=tenant
        )

        results = results.filter(
            tenant=tenant
        )

        student_fees = student_fees.filter(
            tenant=tenant
        )

        fee_payments = fee_payments.filter(
            student_fee__tenant=tenant
        )

        books = books.filter(
            tenant=tenant
        )

        library_issues = library_issues.filter(
            tenant=tenant
        )

    total_students = students.count()
    active_students = students.filter(
        is_active=True
    ).count()
    inactive_students = students.filter(
        is_active=False
    ).count()

    total_teachers = teachers.count()
    active_teachers = teachers.filter(
        is_active=True
    ).count()
    inactive_teachers = teachers.filter(
        is_active=False
    ).count()

    total_classes = classes.count()
    total_subjects = subjects.count()

    total_fee_assigned = (
        student_fees.aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    total_fee_collected = (
        student_fees.aggregate(
            total=Sum("paid_amount")
        )["total"]
        or 0
    )

    total_fee_pending = 0

    for student_fee in student_fees:
        total_fee_pending = total_fee_pending + student_fee.balance_amount

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
        or 0
    )

    total_exams = examinations.count()

    published_exams = examinations.filter(
        is_published=True
    ).count()

    unpublished_exams = examinations.filter(
        is_published=False
    ).count()

    total_results = results.count()

    pass_results = results.filter(
        result_status="PASS"
    ).count()

    fail_results = results.filter(
        result_status="FAIL"
    ).count()

    published_results = results.filter(
        is_published=True
    ).count()

    context = {
        "show_academic_reports": show_academic_reports,
        "show_fee_reports": show_fee_reports,
        "show_library_reports": show_library_reports,
        "show_exam_reports": show_exam_reports,

        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": inactive_students,

        "total_teachers": total_teachers,
        "active_teachers": active_teachers,
        "inactive_teachers": inactive_teachers,

        "total_classes": total_classes,
        "total_subjects": total_subjects,

        "total_fee_assigned": total_fee_assigned,
        "total_fee_collected": total_fee_collected,
        "total_fee_pending": total_fee_pending,
        "pending_fee_count": pending_fee_count,
        "partial_fee_count": partial_fee_count,
        "paid_fee_count": paid_fee_count,
        "total_payments": total_payments,

        "total_books": total_books,
        "total_book_copies": total_book_copies,
        "available_book_copies": available_book_copies,
        "borrowed_books": borrowed_books,
        "returned_books": returned_books,
        "total_library_fines": total_library_fines,

        "total_exams": total_exams,
        "published_exams": published_exams,
        "unpublished_exams": unpublished_exams,
        "total_results": total_results,
        "pass_results": pass_results,
        "fail_results": fail_results,
        "published_results": published_results,
    }

    return render(
        request,
        "core/reports_dashboard.html",
        context,
    )
def can_view_reports(user):

    return (
        user.groups.filter(name="Product Owner").exists()
        or user.groups.filter(name="School Admin").exists()
        or user.groups.filter(name="Accountant").exists()
        or user.groups.filter(name="Librarian").exists()
    )


def is_product_owner(user):

    return user.groups.filter(
        name="Product Owner"
    ).exists()


def is_school_admin(user):

    return user.groups.filter(
        name="School Admin"
    ).exists()


def is_accountant(user):

    return user.groups.filter(
        name="Accountant"
    ).exists()


def is_librarian(user):

    return user.groups.filter(
        name="Librarian"
    ).exists()


def get_current_user_tenant(user):

    if is_product_owner(user):
        return None

    return user.tenant


@login_required
def student_report(request):

    if not is_school_admin(request.user):
        return render(request, "accounts/access_denied.html")

    tenant = get_current_user_tenant(request.user)

    search_query = request.GET.get("q", "")
    class_filter = request.GET.get("class", "")
    status_filter = request.GET.get("status", "")

    students = Student.objects.select_related(
        "tenant",
        "school_class",
        "section",
    )

    classes = SchoolClass.objects.all()

    if tenant is not None:

        students = students.filter(
            tenant=tenant
        )

        classes = classes.filter(
            tenant=tenant
        )

    if search_query:

        students = students.filter(
            Q(student_id__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    if class_filter:

        students = students.filter(
            school_class_id=class_filter
        )

    if status_filter == "active":

        students = students.filter(
            is_active=True
        )

    elif status_filter == "inactive":

        students = students.filter(
            is_active=False
        )

    total_students = students.count()

    active_students = students.filter(
        is_active=True
    ).count()

    inactive_students = students.filter(
        is_active=False
    ).count()

    context = {
        "students": students,
        "classes": classes,
        "search_query": search_query,
        "class_filter": class_filter,
        "status_filter": status_filter,
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": inactive_students,
    }

    return render(
        request,
        "core/student_report.html",
        context,
    )


@login_required
def teacher_report(request):

    if not is_school_admin(request.user):
        return render(request, "accounts/access_denied.html")

    tenant = get_current_user_tenant(request.user)

    search_query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")

    teachers = Teacher.objects.select_related(
        "tenant",
    )

    if tenant is not None:

        teachers = teachers.filter(
            tenant=tenant
        )

    if search_query:

        teachers = teachers.filter(
            Q(teacher_id__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(subject__icontains=search_query)
            | Q(qualification__icontains=search_query)
        )

    if status_filter == "active":

        teachers = teachers.filter(
            is_active=True
        )

    elif status_filter == "inactive":

        teachers = teachers.filter(
            is_active=False
        )

    total_teachers = teachers.count()

    active_teachers = teachers.filter(
        is_active=True
    ).count()

    inactive_teachers = teachers.filter(
        is_active=False
    ).count()

    context = {
        "teachers": teachers,
        "search_query": search_query,
        "status_filter": status_filter,
        "total_teachers": total_teachers,
        "active_teachers": active_teachers,
        "inactive_teachers": inactive_teachers,
    }

    return render(
        request,
        "core/teacher_report.html",
        context,
    )


@login_required
def fee_report(request):

    if not (
        is_school_admin(request.user)
        or is_accountant(request.user)
    ):
        return render(request, "accounts/access_denied.html")

    tenant = get_current_user_tenant(request.user)

    search_query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")

    student_fees = StudentFee.objects.select_related(
        "tenant",
        "student",
        "fee_structure",
        "fee_structure__academic_term",
        "fee_structure__school_class",
    )

    if tenant is not None:

        student_fees = student_fees.filter(
            tenant=tenant
        )

    if search_query:

        student_fees = student_fees.filter(
            Q(student__student_id__icontains=search_query)
            | Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
            | Q(fee_structure__fee_name__icontains=search_query)
        )

    if status_filter:

        student_fees = student_fees.filter(
            status=status_filter
        )

    total_assigned = (
        student_fees.aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    total_collected = (
        student_fees.aggregate(
            total=Sum("paid_amount")
        )["total"]
        or 0
    )

    total_pending = 0

    for fee in student_fees:

        total_pending = (
            total_pending
            + fee.balance_amount
        )

    pending_count = student_fees.filter(
        status="Pending"
    ).count()

    partial_count = student_fees.filter(
        status="Partially Paid"
    ).count()

    paid_count = student_fees.filter(
        status="Paid"
    ).count()

    context = {
        "student_fees": student_fees,
        "search_query": search_query,
        "status_filter": status_filter,
        "total_assigned": total_assigned,
        "total_collected": total_collected,
        "total_pending": total_pending,
        "pending_count": pending_count,
        "partial_count": partial_count,
        "paid_count": paid_count,
    }

    return render(
        request,
        "core/fee_report.html",
        context,
    )


@login_required
def library_report(request):

    if not (
        is_school_admin(request.user)
        or is_librarian(request.user)
    ):
        return render(request, "accounts/access_denied.html")

    tenant = get_current_user_tenant(request.user)

    search_query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")

    issues = LibraryIssue.objects.select_related(
        "tenant",
        "book",
        "student",
        "teacher",
    )

    books = Book.objects.all()

    if tenant is not None:

        issues = issues.filter(
            tenant=tenant
        )

        books = books.filter(
            tenant=tenant
        )

    if search_query:

        issues = issues.filter(
            Q(book__title__icontains=search_query)
            | Q(book__author__icontains=search_query)
            | Q(student__student_id__icontains=search_query)
            | Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
            | Q(teacher__teacher_id__icontains=search_query)
            | Q(teacher__first_name__icontains=search_query)
            | Q(teacher__last_name__icontains=search_query)
        )

    if status_filter:

        issues = issues.filter(
            status=status_filter
        )

    total_books = books.count()

    total_copies = (
        books.aggregate(
            total=Sum("total_copies")
        )["total"]
        or 0
    )

    available_copies = (
        books.aggregate(
            total=Sum("available_copies")
        )["total"]
        or 0
    )

    borrowed_count = issues.filter(
        status="Borrowed"
    ).count()

    returned_count = issues.filter(
        status="Returned"
    ).count()

    lost_count = issues.filter(
        status="Lost"
    ).count()

    total_fines = (
        issues.aggregate(
            total=Sum("fine_amount")
        )["total"]
        or 0
    )

    context = {
        "issues": issues,
        "search_query": search_query,
        "status_filter": status_filter,
        "total_books": total_books,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "borrowed_count": borrowed_count,
        "returned_count": returned_count,
        "lost_count": lost_count,
        "total_fines": total_fines,
    }

    return render(
        request,
        "core/library_report.html",
        context,
    )


@login_required
def exam_result_report(request):

    if not is_school_admin(request.user):
        return render(request, "accounts/access_denied.html")

    tenant = get_current_user_tenant(request.user)

    search_query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")

    results = Result.objects.select_related(
        "tenant",
        "student",
        "student__school_class",
        "student__section",
        "academic_term",
        "academic_term__academic_year",
    )

    examinations = Examination.objects.select_related(
        "tenant",
        "academic_term",
        "school_class",
        "subject",
    )

    if tenant is not None:

        results = results.filter(
            tenant=tenant
        )

        examinations = examinations.filter(
            tenant=tenant
        )

    if search_query:

        results = results.filter(
            Q(student__student_id__icontains=search_query)
            | Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
            | Q(academic_term__term_name__icontains=search_query)
        )

    if status_filter:

        results = results.filter(
            result_status=status_filter
        )

    total_exams = examinations.count()

    published_exams = examinations.filter(
        is_published=True
    ).count()

    unpublished_exams = examinations.filter(
        is_published=False
    ).count()

    total_results = results.count()

    pass_count = results.filter(
        result_status="PASS"
    ).count()

    fail_count = results.filter(
        result_status="FAIL"
    ).count()

    published_results = results.filter(
        is_published=True
    ).count()

    context = {
        "results": results,
        "search_query": search_query,
        "status_filter": status_filter,
        "total_exams": total_exams,
        "published_exams": published_exams,
        "unpublished_exams": unpublished_exams,
        "total_results": total_results,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "published_results": published_results,
    }

    return render(
        request,
        "core/exam_result_report.html",
        context,
    )
def can_manage_announcements(user):

    return user.groups.filter(
        name="School Admin"
    ).exists()


def can_view_announcements(user):

    return (
        user.groups.filter(name="School Admin").exists()
        or user.groups.filter(name="Teacher").exists()
        or user.groups.filter(name="Student").exists()
        or user.groups.filter(name="Accountant").exists()
        or user.groups.filter(name="Librarian").exists()
    )


def get_user_role_name(user):

    if user.groups.exists():

        return user.groups.first().name

    return ""


@login_required
def announcements(request):

    if not can_view_announcements(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    role_name = get_user_role_name(
        request.user
    )

    today = timezone.localdate()

    search_query = request.GET.get("q", "")
    target_filter = request.GET.get("target", "")
    priority_filter = request.GET.get("priority", "")

    announcement_list = Announcement.objects.filter(
        tenant=request.user.tenant,
    ).select_related(
        "tenant",
        "created_by",
    )

    if not can_manage_announcements(request.user):

        announcement_list = announcement_list.filter(
            is_active=True,
            start_date__lte=today,
        ).filter(
            Q(end_date__isnull=True)
            | Q(end_date__gte=today)
        ).filter(
            Q(target_role="All")
            | Q(target_role=role_name)
        )

    if search_query:

        announcement_list = announcement_list.filter(
            Q(title__icontains=search_query)
            | Q(message__icontains=search_query)
        )

    if target_filter:

        announcement_list = announcement_list.filter(
            target_role=target_filter
        )

    if priority_filter:

        announcement_list = announcement_list.filter(
            priority=priority_filter
        )

    context = {
        "announcements": announcement_list,
        "search_query": search_query,
        "target_filter": target_filter,
        "priority_filter": priority_filter,
        "can_manage": can_manage_announcements(request.user),
    }

    return render(
        request,
        "core/announcements.html",
        context,
    )


@login_required
def add_announcement(request):

    if not can_manage_announcements(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    if request.method == "POST":

        form = AnnouncementForm(
            request.POST,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Announcement created successfully.",
            )

            return redirect(
                "core:announcements"
            )

    else:

        form = AnnouncementForm(
            current_user=request.user,
            initial={
                "start_date": timezone.localdate(),
                "target_role": "All",
                "priority": "Normal",
            },
        )

    context = {
        "form": form,
        "title": "Add Announcement",
        "button_text": "Save Announcement",
    }

    return render(
        request,
        "core/announcement_form.html",
        context,
    )


@login_required
def edit_announcement(request, announcement_id):

    if not can_manage_announcements(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    announcement = get_object_or_404(
        Announcement,
        id=announcement_id,
        tenant=request.user.tenant,
    )

    if request.method == "POST":

        form = AnnouncementForm(
            request.POST,
            instance=announcement,
            current_user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Announcement updated successfully.",
            )

            return redirect(
                "core:announcements"
            )

    else:

        form = AnnouncementForm(
            instance=announcement,
            current_user=request.user,
        )

    context = {
        "form": form,
        "title": "Edit Announcement",
        "button_text": "Update Announcement",
    }

    return render(
        request,
        "core/announcement_form.html",
        context,
    )


@login_required
def toggle_announcement_status(request, announcement_id):

    if not can_manage_announcements(request.user):
        return render(
            request,
            "accounts/access_denied.html",
        )

    announcement = get_object_or_404(
        Announcement,
        id=announcement_id,
        tenant=request.user.tenant,
    )

    announcement.is_active = not announcement.is_active

    announcement.save()

    if announcement.is_active:

        messages.success(
            request,
            "Announcement activated successfully.",
        )

    else:

        messages.warning(
            request,
            "Announcement deactivated successfully.",
        )

    return redirect(
        "core:announcements"
    )