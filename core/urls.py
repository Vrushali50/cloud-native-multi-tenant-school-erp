from django.urls import path

from .views import(
    students,
    teachers,
    academic_years,
    add_academic_year,
    edit_academic_year,
    classes,
    add_class,
    edit_class,
    sections,
    add_section,
    edit_section,
    subjects,
    add_subject,
    edit_subject,
    teacher_assignments,
    add_teacher_assignment,
    edit_teacher_assignment,
    add_student,
    edit_student,
    student_profile,
    toggle_student_status,
    add_teacher,
    edit_teacher,
    teacher_profile,
    toggle_teacher_status,
    record_student_attendance,
    student_attendance_records,
    staff_attendance,
    staff_attendance_report,
    timetables,
    add_timetable,
    edit_timetable,
    delete_timetable,
    student_timetable,
    teacher_timetable,
    examinations,
    add_examination,
    edit_examination,
    delete_examination,
    toggle_exam_publish,
    manage_exam_halls,
    add_exam_hall,
    edit_exam_hall,
    delete_exam_hall,
    teacher_invigilation,
    student_examinations,
    teacher_marks,
    enter_marks,
    assignment_examinations,
    results,
    generate_results,
    toggle_result_publish,
    teacher_results,
    student_results,
    result_details,
    print_report_card,
    fee_structures,
    add_fee_structure,
    edit_fee_structure,
    student_fees,
    assign_student_fee,
    collect_fee_payment,
    fee_payments,
    bulk_assign_student_fee,
    my_fees,
    book_categories,
    add_book_category,
    edit_book_category,
    books,
    add_book,
    edit_book,
    library_issues,
    issue_book,
    return_book,
    my_library_records,
    reports_dashboard,
    student_report,
    teacher_report,
    fee_report,
    library_report,
    exam_result_report,
    announcements,
    add_announcement,
    edit_announcement,
    toggle_announcement_status,
    academic_terms,
    add_academic_term,
    edit_academic_term,
    set_current_academic_term,
)


app_name = "core"


urlpatterns = [
    path(
        "students/",
        students,
        name="students",
    ),

    path(
        "teachers/",
        teachers,
        name="teachers",
    ),

    path(
        "academic-years/",
        academic_years,
        name="academic_years",
    ),

    path(
        "academic-years/add/",
        add_academic_year,
        name="add_academic_year",
    ),

    path(
        "academic-years/<int:academic_year_id>/edit/",
        edit_academic_year,
        name="edit_academic_year",
    ),
    path("academic-terms/", academic_terms, name="academic_terms"),
    path("academic-terms/add/", add_academic_term, name="add_academic_term"),
    path("academic-terms/<int:term_id>/edit/", edit_academic_term, name="edit_academic_term"),
    path("academic-terms/<int:term_id>/set-current/", set_current_academic_term, name="set_current_academic_term"),
    path(
        "classes/",
        classes,
        name="classes",
    ),


    path(
    "classes/add/",
    add_class,
    name="add_class",
    ),

    path(
    "classes/<int:class_id>/edit/",
    edit_class,
    name="edit_class",
    ),

    path(
    "sections/",
    sections,
    name="sections",
    ),

    path(
        "sections/add/",
        add_section,
        name="add_section",
        ),

    path(
        "sections/<int:section_id>/edit/",
        edit_section,
        name="edit_section",
        ),

    path(
        "subjects/",
        subjects,
        name="subjects",
        ),

    path(
        "subjects/add/",
        add_subject,
        name="add_subject",
        ),

    path(
            "subjects/<int:subject_id>/edit/",
            edit_subject,
            name="edit_subject",
        ),

    path(
        "teacher-assignments/",
        teacher_assignments,
        name="teacher_assignments",
    ),

    path(
        "teacher-assignments/add/",
        add_teacher_assignment,
        name="add_teacher_assignment",
    ),

    path(
        "teacher-assignments/<int:assignment_id>/edit/",
        edit_teacher_assignment,
        name="edit_teacher_assignment",
    ),

    path(
        "students/add/",
        add_student,
        name="add_student",
    ),

    path(
        "students/<int:student_id>/",
        student_profile,
        name="student_profile",
    ),

    path(
        "students/<int:student_id>/edit/",
        edit_student,
        name="edit_student",
    ),

    path(
        "students/<int:student_id>/status/",
        toggle_student_status,
        name="toggle_student_status",
    ),

    path(
        "teachers/add/",
        add_teacher,
        name="add_teacher",
    ),

    path(
        "teachers/<int:teacher_id>/",
        teacher_profile,
        name="teacher_profile",
    ),

    path(
        "teachers/<int:teacher_id>/edit/",
        edit_teacher,
        name="edit_teacher",
    ),

    path(
        "teachers/<int:teacher_id>/status/",
        toggle_teacher_status,
        name="toggle_teacher_status",
    ),

    path(
        "attendance/students/record/",
        record_student_attendance,
        name="record_student_attendance",
    ),

    path(
        "attendance/students/",
        student_attendance_records,
        name="student_attendance_records",
    ),
    path(
        "staff-attendance/",
        staff_attendance,
        name="staff_attendance",
    ),
    path(
        "staff-attendance-report/",
        staff_attendance_report,
        name="staff_attendance_report",
    ),
    path(
        "student/timetable/",
        student_timetable,
        name="student_timetable",
    ),
    path(
        "teacher/timetable/",
        teacher_timetable,
        name="teacher_timetable",
    ),
    path(
        "timetables/",
        timetables,
        name="timetables",
    ),


    path(
        "timetables/add/",
        add_timetable,
        name="add_timetable",
    ),

    path(
        "timetables/<int:timetable_id>/edit/",
        edit_timetable,
        name="edit_timetable",
    ),

    path(
        "timetables/<int:timetable_id>/delete/",
        delete_timetable,
        name="delete_timetable",
    ),
    path(
        "examinations/",
        examinations,
        name="examinations",
    ),

    path(
        "examinations/add/",
        add_examination,
        name="add_examination",
    ),

    path(
        "examinations/<int:examination_id>/edit/",
        edit_examination,
        name="edit_examination",
    ),

    path(
        "examinations/<int:examination_id>/delete/",
        delete_examination,
        name="delete_examination",
    ),

    path(
        "examinations/<int:examination_id>/publish/",
        toggle_exam_publish,
        name="toggle_exam_publish",
    ),

    path(
        "examinations/<int:examination_id>/halls/",
        manage_exam_halls,
        name="manage_exam_halls",
    ),

    path(
        "examinations/<int:examination_id>/halls/add/",
        add_exam_hall,
        name="add_exam_hall",
    ),

    path(
        "hall-allocation/<int:allocation_id>/edit/",
        edit_exam_hall,
        name="edit_exam_hall",
    ),

    path(
        "hall-allocation/<int:allocation_id>/delete/",
        delete_exam_hall,
        name="delete_exam_hall",
    ),
    path(
        "teacher/invigilation/",
        teacher_invigilation,
        name="teacher_invigilation",
    ),
    path(
        "student/examinations/",
        student_examinations,
        name="student_examinations",
    ),
    path(
        "teacher/marks/",
        teacher_marks,
        name="teacher_marks",
    ),

    path(
        "teacher/marks/<int:assignment_id>/<int:examination_id>/",
        enter_marks,
        name="enter_marks",
    ),
    path(
        "teacher/marks/<int:assignment_id>/examinations/",
        assignment_examinations,
        name="assignment_examinations",
    ),
    path(
        "results/",
        results,
        name="results",
    ),

    path(
        "results/generate/<int:academic_term_id>/",
        generate_results,
        name="generate_results",
    ),

    path(
        "results/publish/<int:result_id>/",
        toggle_result_publish,
        name="toggle_result_publish",
    ),

    path(
        "teacher/results/",
        teacher_results,
        name="teacher_results",
    ),
    path(
        "student/results/",
        student_results,
        name="student_results",
    ),
    path(
        "results/details/<int:result_id>/",
        result_details,
        name="result_details",
    ),
    path(
        "results/<int:result_id>/print/",
        print_report_card,
        name="print_report_card",
    ),
    path("fees/structures/", fee_structures, name="fee_structures"),
    path("fees/structures/add/", add_fee_structure, name="add_fee_structure"),
    path("fees/structures/<int:fee_structure_id>/edit/", edit_fee_structure, name="edit_fee_structure"),

    path("fees/student-fees/", student_fees, name="student_fees"),
    path("fees/student-fees/assign/", assign_student_fee, name="assign_student_fee"),
    path("fees/student-fees/<int:student_fee_id>/collect/", collect_fee_payment, name="collect_fee_payment"),

    path("fees/payments/", fee_payments, name="fee_payments"),
    path("fees/student-fees/bulk-assign/", bulk_assign_student_fee, name="bulk_assign_student_fee"),
    path("fees/my-fees/", my_fees, name="my_fees"),
    path("library/categories/", book_categories, name="book_categories"),
    path("library/categories/add/", add_book_category, name="add_book_category"),
    path("library/categories/<int:category_id>/edit/", edit_book_category, name="edit_book_category"),

    path("library/books/", books, name="books"),
    path("library/books/add/", add_book, name="add_book"),
    path("library/books/<int:book_id>/edit/", edit_book, name="edit_book"),

    path("library/issues/", library_issues, name="library_issues"),
    path("library/issues/issue/", issue_book, name="issue_book"),
    path("library/issues/<int:issue_id>/return/", return_book, name="return_book"),

    path("library/my-records/", my_library_records, name="my_library_records"),
    path("reports/", reports_dashboard, name="reports_dashboard"),

    path("reports/students/", student_report, name="student_report"),
    path("reports/teachers/", teacher_report, name="teacher_report"),
    path("reports/fees/", fee_report, name="fee_report"),
    path("reports/library/", library_report, name="library_report"),
    path("reports/exams-results/", exam_result_report, name="exam_result_report"),

    path("announcements/", announcements, name="announcements"),
    path("announcements/add/", add_announcement, name="add_announcement"),
    path("announcements/<int:announcement_id>/edit/", edit_announcement, name="edit_announcement"),
    path("announcements/<int:announcement_id>/toggle-status/", toggle_announcement_status, name="toggle_announcement_status"),
]