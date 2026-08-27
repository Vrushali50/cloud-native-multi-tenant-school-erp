from django.conf import settings
from django.db import models
from tenants.models import Tenant
from decimal import Decimal
from datetime import datetime




class Student(models.Model):
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="students",
    )

    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="student_profile",
    null=True,
    blank=True,
    )

    school_class = models.ForeignKey(
    "SchoolClass",
    on_delete=models.SET_NULL,
    related_name="students",
    null=True,
    blank=True,
    )

    section = models.ForeignKey(
    "Section",
    on_delete=models.SET_NULL,
    related_name="students",
    null=True,
    blank=True,
    )

    admission_number = models.CharField(
    max_length=30,
    unique=True,
    null=True,
    blank=True,
    )

    student_id = models.CharField(
        max_length=20,
        unique=True,
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
    )

    address = models.TextField()
    admission_date = models.DateField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"


class Teacher(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="teachers",
    )

    teacher_id = models.CharField(
        max_length=20,
        unique=True,
    )


    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="teacher_profile",
    null=True,
    blank=True,
)

    employee_number = models.CharField(
    max_length=30,
    unique=True,
    null=True,
    blank=True,
)

    qualification = models.CharField(
    max_length=150,
    blank=True,
)

    hire_date = models.DateField(
    null=True,
    blank=True,
)

    is_active = models.BooleanField(
    default=True,
)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    subject = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.teacher_id} - {self.first_name} {self.last_name}"




class AcademicYear(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="academic_years",
    )

    year_name = models.CharField(
        max_length=20,
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_current = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.year_name
class AcademicTerm(models.Model):

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="terms",
    )

    term_name = models.CharField(
        max_length=100,
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_current = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.term_name

class SchoolClass(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="classes",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="classes",
    )

    class_name = models.CharField(
        max_length=100,
    )

    def __str__(self):
        return self.class_name

class Section(models.Model):
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="sections",
    )

    section_name = models.CharField(
        max_length=50,
    )

    def __str__(self):
        return f"{self.school_class.class_name} - {self.section_name}"

class Subject(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="subjects",
    )

    subject_name = models.CharField(
        max_length=100,
    )

    subject_code = models.CharField(
        max_length=20,
    )

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"

class TeacherSubject(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    def __str__(self):
        return (
            f"{self.teacher} - "
            f"{self.subject} - "
            f"{self.school_class}"
        )

class StudentAttendance(models.Model):

    STATUS_CHOICES = (
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Late", "Late"),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="student_attendance",
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    teacher_subject = models.ForeignKey(
        TeacherSubject,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    attendance_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "teacher_subject",
                    "attendance_date",
                ],
                name="unique_student_attendance",
            )
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.attendance_date} - "
            f"{self.status}"
        )


class StaffAttendance(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="staff_attendance",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_attendance_records",
    )

    attendance_date = models.DateField()

    check_in_time = models.TimeField(
        null=True,
        blank=True,
    )

    check_out_time = models.TimeField(
        null=True,
        blank=True,
    )

    hours_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "attendance_date",
                ],
                name="unique_staff_attendance",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.attendance_date}"
        )
class Timetable(models.Model):

    DAYS = (
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="timetables",
    )

    academic_term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        related_name="timetables",
    )

    teacher_assignment = models.ForeignKey(
        TeacherSubject,
        on_delete=models.CASCADE,
        related_name="timetables",
    )

    day = models.CharField(
        max_length=20,
        choices=DAYS,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    room_number = models.CharField(
        max_length=20,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "day",
            "start_time",
        ]

    def __str__(self):

        return (
            f"{self.teacher_assignment.subject.subject_name}"
            f" - "
            f"{self.teacher_assignment.school_class.class_name}"
            f" - "
            f"{self.day}"
        )
class Examination(models.Model):

    EXAM_TYPE_CHOICES = (
        ("Mid Term", "Mid Term"),
        ("Final Exam", "Final Exam"),
        ("Unit Test", "Unit Test"),
        ("Quiz", "Quiz"),
        ("Practical", "Practical"),
        ("Assignment", "Assignment"),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="examinations",
    )

    academic_term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        related_name="examinations",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="examinations",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="examinations",
    )

    exam_type = models.CharField(
        max_length=30,
        choices=EXAM_TYPE_CHOICES,
    )

    exam_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    total_marks = models.PositiveIntegerField()

    passing_marks = models.PositiveIntegerField()

    instructions = models.TextField(
        blank=True,
    )

    is_published = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "exam_date",
            "start_time",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "academic_term",
                    "school_class",
                    "subject",
                    "exam_type",
                ],

                name="unique_exam_per_subject",

            ),

        ]

    @property
    def exam_name(self):

        return (
            f"{self.subject.subject_name}"
            f" - "
            f"{self.exam_type}"
        )

    def __str__(self):

        return self.exam_name
class ExamHallAllocation(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="exam_hall_allocations",
    )

    examination = models.ForeignKey(
        Examination,
        on_delete=models.CASCADE,
        related_name="hall_allocations",
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="exam_hall_allocations",
    )

    hall_name = models.CharField(
        max_length=100,
    )

    invigilator = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="invigilations",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "section",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "examination",
                    "section",
                ],

                name="unique_section_exam_allocation",

            ),

        ]

    def __str__(self):

        return (
            f"{self.examination.exam_name}"
            f" - "
            f"{self.section.section_name}"
        )
class StudentMark(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="student_marks",
    )

    examination = models.ForeignKey(
        Examination,
        on_delete=models.CASCADE,
        related_name="student_marks",
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="marks",
    )

    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    remarks = models.TextField(
        blank=True,
    )

    entered_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entered_marks",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "student",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "examination",
                    "student",
                ],

                name="unique_student_exam_mark",

            ),

        ]

    def __str__(self):

        return (
            f"{self.student.first_name} "
            f"{self.student.last_name}"
            f" - "
            f"{self.examination.exam_name}"
        )
class Result(models.Model):

    RESULT_STATUS = [

        ("PASS", "Pass"),

        ("FAIL", "Fail"),

    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="results",
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="results",
    )

    academic_term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        related_name="results",
    )

    total_marks = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    grade = models.CharField(
        max_length=5,
        blank=True,
    )

    result_status = models.CharField(
        max_length=10,
        choices=RESULT_STATUS,
        default="FAIL",
    )

    is_published = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "student",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "student",
                    "academic_term",
                ],

                name="unique_student_result",

            ),

        ]

    def __str__(self):

        return (

            f"{self.student.first_name} "

            f"{self.student.last_name}"

            f" - "

            f"{self.academic_term.term_name}"

        )
class FeeStructure(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )

    academic_term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )

    fee_name = models.CharField(
        max_length=100,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    due_date = models.DateField()

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "due_date",
            "fee_name",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "tenant",
                    "academic_term",
                    "school_class",
                    "fee_name",
                ],

                name="unique_fee_structure",

            ),

        ]

    def __str__(self):

        return (
            f"{self.fee_name} - "
            f"{self.school_class.class_name} - "
            f"{self.academic_term.term_name}"
        )


class StudentFee(models.Model):

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Partially Paid", "Partially Paid"),
        ("Paid", "Paid"),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="student_fees",
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="student_fees",
    )

    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name="student_fees",
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "student",
            "fee_structure",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "student",
                    "fee_structure",
                ],

                name="unique_student_fee_assignment",

            ),

        ]

    @property
    def balance_amount(self):

        balance = self.total_amount - self.paid_amount

        if balance < 0:
            return Decimal("0.00")

        return balance

    def save(self, *args, **kwargs):

        if self.paid_amount <= 0:

            self.status = "Pending"

        elif self.paid_amount < self.total_amount:

            self.status = "Partially Paid"

        else:

            self.status = "Paid"

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.student.first_name} "
            f"{self.student.last_name} - "
            f"{self.fee_structure.fee_name}"
        )


class FeePayment(models.Model):

    PAYMENT_METHODS = (
        ("Cash", "Cash"),
        ("Card", "Card"),
        ("Bank Transfer", "Bank Transfer"),
        ("Online", "Online"),
    )

    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    payment_date = models.DateField()

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHODS,
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_fee_payments",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-payment_date",
            "-created_at",
        ]

    def __str__(self):

        return (
            f"{self.student_fee.student.first_name} "
            f"{self.student_fee.student.last_name} - "
            f"{self.amount_paid}"
        )
class BookCategory(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="book_categories",
    )

    category_name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["category_name"]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "category_name"],
                name="unique_book_category_per_tenant",
            )
        ]

    def __str__(self):
        return self.category_name


class Book(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="books",
    )

    category = models.ForeignKey(
        BookCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
    )

    title = models.CharField(
        max_length=200,
    )

    author = models.CharField(
        max_length=150,
    )

    isbn = models.CharField(
        max_length=30,
        blank=True,
    )

    publisher = models.CharField(
        max_length=150,
        blank=True,
    )

    publication_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    total_copies = models.PositiveIntegerField(
        default=1,
    )

    available_copies = models.PositiveIntegerField(
        default=1,
    )

    shelf_location = models.CharField(
        max_length=100,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["title", "author"]

    def __str__(self):
        return f"{self.title} - {self.author}"


class LibraryIssue(models.Model):

    MEMBER_TYPE_CHOICES = (
        ("Student", "Student"),
        ("Teacher", "Teacher"),
    )

    STATUS_CHOICES = (
        ("Borrowed", "Borrowed"),
        ("Returned", "Returned"),
        ("Lost", "Lost"),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="library_issues",
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="library_issues",
    )

    member_type = models.CharField(
        max_length=20,
        choices=MEMBER_TYPE_CHOICES,
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="library_issues",
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="library_issues",
    )

    issue_date = models.DateField()

    due_date = models.DateField()

    return_date = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Borrowed",
    )

    fine_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_library_books",
    )

    returned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="returned_library_books",
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-issue_date", "-created_at"]

    @property
    def member_name(self):

        if self.member_type == "Student" and self.student:
            return f"{self.student.first_name} {self.student.last_name}"

        if self.member_type == "Teacher" and self.teacher:
            return f"{self.teacher.first_name} {self.teacher.last_name}"

        return "-"

    def __str__(self):
        return f"{self.book.title} - {self.member_name}"
class Announcement(models.Model):

    TARGET_ROLE_CHOICES = (
        ("All", "All"),
        ("School Admin", "School Admin"),
        ("Teacher", "Teacher"),
        ("Student", "Student"),
        ("Accountant", "Accountant"),
        ("Librarian", "Librarian"),
    )

    PRIORITY_CHOICES = (
        ("Low", "Low"),
        ("Normal", "Normal"),
        ("High", "High"),
        ("Urgent", "Urgent"),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="announcements",
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    target_role = models.CharField(
        max_length=30,
        choices=TARGET_ROLE_CHOICES,
        default="All",
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="Normal",
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_announcements",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.title