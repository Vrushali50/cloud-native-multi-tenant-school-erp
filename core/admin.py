from django.contrib import admin

from .models import Student, Teacher


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