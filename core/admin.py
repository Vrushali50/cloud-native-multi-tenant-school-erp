from django.contrib import admin

from .models import Student, Teacher, AcademicYear, SchoolClass, Section, Subject, TeacherSubject, StudentAttendance, StaffAttendance, Timetable, AcademicTerm, Examination, ExamHallAllocation, StudentMark, Result, FeeStructure, StudentFee, FeePayment, BookCategory, Book, LibraryIssue, Announcement

    

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "is_active",
    )

    search_fields = (
        "student_id",
        "first_name",
        "last_name",
        "email",
    )

    list_filter = (
        "gender",
        "is_active",
    )


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "teacher_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "subject",
    )

    search_fields = (
        "teacher_id",
        "first_name",
        "last_name",
        "email",
        "subject",
    )

    list_filter = (
        "subject",
        "tenant",
    )

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = (
        "year_name",
        "tenant",
        "start_date",
        "end_date",
        "is_current",
    )

    search_fields = (
        "year_name",
    )

    list_filter = (
        "tenant",
        "is_current",
    )
@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):

    list_display = (
        "academic_year",
        "term_name",
        "start_date",
        "end_date",
        "is_current",
    )

    search_fields = (
        "term_name",
        "academic_year__year_name",
    )

    list_filter = (
        "academic_year",
        "is_current",
    )
@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = (
        "class_name",
        "tenant",
        "academic_year",
    )

    list_filter = (
        "tenant",
        "academic_year",
    )

    search_fields = (
        "class_name",
    )

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "section_name",
        "school_class",
    )

    list_filter = (
        "school_class",
    )

    search_fields = (
        "section_name",
    )

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "subject_code",
        "subject_name",
        "tenant",
    )

    search_fields = (
        "subject_code",
        "subject_name",
    )

    list_filter = (
        "tenant",
    )


@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "subject",
        "school_class",
        "section",
        "academic_year",
    )

    list_filter = (
        "academic_year",
        "school_class",
        "subject",
    )

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "teacher_subject",
        "attendance_date",
        "status",
    )

    list_filter = (
        "status",
        "attendance_date",
        "tenant",
    )

    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__student_id",
    )
@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "attendance_date",
        "check_in_time",
        "check_out_time",
        "hours_worked",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    list_filter = (
        "tenant",
        "attendance_date",
    )
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):

    list_display = (
        "teacher_assignment",
        "day",
        "start_time",
        "end_time",
        "room_number",
    )

    search_fields = (
        "teacher_assignment__teacher__first_name",
        "teacher_assignment__teacher__last_name",
        "teacher_assignment__subject__subject_name",
        "teacher_assignment__school_class__class_name",
    )

    list_filter = (
        "tenant",
        "day",
    )
@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):

    list_display = (
        "exam_name",
        "tenant",
        "school_class",
        "subject",
        "exam_type",
        "exam_date",
        "is_published",
    )

    search_fields = (
        "subject__subject_name",
        "school_class__class_name",
        "academic_term__term_name",
        "tenant__school_name",
    )

    list_filter = (
        "academic_term",
        "school_class",
        "exam_type",
        "is_published",
    )

    ordering = (
        "exam_date",
        "start_time",
    )
@admin.register(ExamHallAllocation)
class ExamHallAllocationAdmin(admin.ModelAdmin):

    list_display = (
        "examination",
        "tenant",
        "section",
        "hall_name",
        "invigilator",
    )

    search_fields = (
        "examination__subject__subject_name",
        "section__section_name",
        "hall_name",
        "invigilator__first_name",
        "invigilator__last_name",
        "tenant__school_name",
    )

    list_filter = (
        "section",
        "invigilator",
    )

    ordering = (
        "examination",
        "section",
    )
@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "examination",
        "marks_obtained",
        "entered_by",
    )

    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__student_id",
        "examination__subject__subject_name",
    )

    list_filter = (
        "examination",
    )

    ordering = (
        "student",
    )
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):

    list_display = (

        "student",

        "academic_term",

        "total_marks",

        "percentage",

        "grade",

        "result_status",

        "is_published",

    )

    search_fields = (

        "student__student_id",

        "student__first_name",

        "student__last_name",

    )

    list_filter = (

        "academic_term",

        "result_status",

        "is_published",

    )

    ordering = (

        "student",

    )
@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):

    list_display = (
        "fee_name",
        "tenant",
        "school_class",
        "academic_term",
        "amount",
        "due_date",
        "is_active",
    )

    search_fields = (
        "fee_name",
        "school_class__class_name",
        "academic_term__term_name",
    )

    list_filter = (
        "tenant",
        "academic_term",
        "school_class",
        "is_active",
    )

    ordering = (
        "due_date",
        "fee_name",
    )


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "fee_structure",
        "total_amount",
        "paid_amount",
        "balance_amount",
        "status",
    )

    search_fields = (
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "fee_structure__fee_name",
    )

    list_filter = (
        "tenant",
        "status",
        "fee_structure",
    )

    ordering = (
        "student",
    )


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):

    list_display = (
        "student_fee",
        "amount_paid",
        "payment_date",
        "payment_method",
        "recorded_by",
    )

    search_fields = (
        "student_fee__student__student_id",
        "student_fee__student__first_name",
        "student_fee__student__last_name",
        "reference_number",
    )

    list_filter = (
        "payment_method",
        "payment_date",
    )

    ordering = (
        "-payment_date",
    )
@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "category_name",
        "tenant",
        "is_active",
        "created_at",
    )

    search_fields = (
        "category_name",
        "description",
    )

    list_filter = (
        "tenant",
        "is_active",
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "author",
        "tenant",
        "category",
        "total_copies",
        "available_copies",
        "is_active",
    )

    search_fields = (
        "title",
        "author",
        "isbn",
        "publisher",
    )

    list_filter = (
        "tenant",
        "category",
        "is_active",
    )


@admin.register(LibraryIssue)
class LibraryIssueAdmin(admin.ModelAdmin):

    list_display = (
        "book",
        "member_type",
        "member_name",
        "issue_date",
        "due_date",
        "return_date",
        "status",
        "fine_amount",
    )

    search_fields = (
        "book__title",
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "teacher__teacher_id",
        "teacher__first_name",
        "teacher__last_name",
    )

    list_filter = (
        "tenant",
        "member_type",
        "status",
        "issue_date",
        "due_date",
    )
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "tenant",
        "target_role",
        "priority",
        "start_date",
        "end_date",
        "is_active",
        "created_by",
    )

    search_fields = (
        "title",
        "message",
    )

    list_filter = (
        "tenant",
        "target_role",
        "priority",
        "is_active",
        "start_date",
    )

    ordering = (
        "-created_at",
    )