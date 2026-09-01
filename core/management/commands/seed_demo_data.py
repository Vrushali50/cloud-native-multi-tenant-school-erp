from datetime import date, timedelta, time
from decimal import Decimal

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import timezone


DEMO_PASSWORD = "Demo@12345"


class Command(BaseCommand):
    help = "Create demo data for the multi-tenant school ERP system."

    def add_arguments(self, parser):
        parser.add_argument(
            "--quick",
            action="store_true",
            help="Create a smaller demo dataset.",
        )

    def handle(self, *args, **options):
        self.quick = options["quick"]

        with transaction.atomic():
            self.stdout.write(self.style.WARNING("Creating demo ERP data..."))

            self.create_groups()

            Tenant = self.get_model("tenants", "Tenant")
            if Tenant is None:
                self.stdout.write(self.style.ERROR("Tenant model not found. Check tenants app."))
                return

            school_a = self.create_tenant(
                Tenant,
                name="Green Valley International School",
                code="GVIS",
                email="admin@gvis.example.com",
            )

            school_b = self.create_tenant(
                Tenant,
                name="Riverdale Public School",
                code="RPS",
                email="admin@rps.example.com",
            )

            self.product_owner = self.create_user(
                username="product_owner",
                email="productowner@example.com",
                first_name="Product",
                last_name="Owner",
                role="Product Owner",
                tenant=None,
                is_staff=True,
            )

            self.create_school_dataset(
                tenant=school_a,
                prefix="gvis",
                school_short_name="GVIS",
                admin_name=("Aarav", "Sharma"),
            )

            self.create_school_dataset(
                tenant=school_b,
                prefix="rps",
                school_short_name="RPS",
                admin_name=("Priya", "Patel"),
            )

            self.seed_remaining_empty_core_models()

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
        self.stdout.write(self.style.SUCCESS(f"Demo password for all users: {DEMO_PASSWORD}"))

    # -------------------------------------------------
    # Basic helpers
    # -------------------------------------------------

    def get_model(self, app_label, model_name):
        try:
            return apps.get_model(app_label, model_name)
        except LookupError:
            return None

    def has_field(self, model, field_name):
        return field_name in [field.name for field in model._meta.fields]

    def get_field(self, model, field_name):
        try:
            return model._meta.get_field(field_name)
        except Exception:
            return None

    def set_field(self, model, data, field_names, value):
        for field_name in field_names:
            if self.has_field(model, field_name):
                data[field_name] = value
                return field_name
        return None

    def clean_data(self, model, data):
        valid_fields = [field.name for field in model._meta.fields]
        return {key: value for key, value in data.items() if key in valid_fields}

    def find_existing_object(self, model, lookup, data):
        lookup = self.clean_data(model, lookup)

        if lookup:
            obj = model.objects.filter(**lookup).first()
            if obj:
                return obj

        for field in model._meta.fields:
            if getattr(field, "unique", False) and field.name in data and data[field.name] is not None:
                obj = model.objects.filter(**{field.name: data[field.name]}).first()
                if obj:
                    return obj

        return None

    def create_or_update(self, model, lookup=None, defaults=None):
        lookup = lookup or {}
        defaults = defaults or {}

        data = {}
        data.update(lookup)
        data.update(defaults)
        data = self.clean_data(model, data)

        self.complete_required_fields(model, data)

        obj = self.find_existing_object(model, lookup, data)

        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
            return obj

        return model.objects.create(**data)

    def complete_required_fields(self, model, data):
        for field in model._meta.fields:
            if field.name in data:
                continue

            if field.primary_key:
                continue

            if getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
                continue

            if field.has_default():
                continue

            if field.null or field.blank:
                continue

            value = self.default_value_for_field(model, field)
            if value is not None:
                data[field.name] = value

    def default_value_for_field(self, model, field):
        field_name = field.name.lower()
        model_name = model.__name__.lower()

        if isinstance(field, (models.ForeignKey, models.OneToOneField)):
            related_model = field.remote_field.model
            related_obj = related_model.objects.first()
            if related_obj:
                return related_obj
            return None

        if isinstance(field, models.EmailField):
            return f"demo_{model_name}_{field_name}@example.com"

        if isinstance(field, models.CharField):
            choice_value = self.first_choice_value(field)
            if choice_value is not None:
                return choice_value

            if "status" in field_name:
                return "Active"
            if "gender" in field_name:
                return "Female"
            if "phone" in field_name:
                return "07123456789"
            if "code" in field_name:
                return "DEMO"
            if "name" in field_name:
                return f"Demo {model.__name__}"
            if "title" in field_name:
                return f"Demo {model.__name__}"
            if "type" in field_name:
                return "General"
            if "role" in field_name:
                return "All"

            value = f"Demo {field.name}"
            max_length = getattr(field, "max_length", None)
            if max_length:
                return value[:max_length]
            return value

        if isinstance(field, models.TextField):
            return f"Demo text for {model.__name__}"

        if isinstance(field, models.BooleanField):
            return True

        if isinstance(field, models.DateField) and not isinstance(field, models.DateTimeField):
            return date.today()

        if isinstance(field, models.DateTimeField):
            return timezone.now()

        if isinstance(field, models.TimeField):
            return time(9, 0)

        if isinstance(field, models.DecimalField):
            return Decimal("100.00")

        if isinstance(field, (models.IntegerField, models.PositiveIntegerField, models.PositiveSmallIntegerField)):
            return 1

        if isinstance(field, models.FloatField):
            return 1.0

        return None

    def first_choice_value(self, field):
        if not field.choices:
            return None

        for choice in field.choices:
            if isinstance(choice, (list, tuple)):
                value = choice[0]
                if value not in ["", None]:
                    return value

        return None

    # -------------------------------------------------
    # Groups and users
    # -------------------------------------------------

    def create_groups(self):
        roles = [
            "Product Owner",
            "School Admin",
            "Teacher",
            "Student",
            "Accountant",
            "Librarian",
        ]

        for role in roles:
            Group.objects.get_or_create(name=role)

    def create_user(self, username, email, first_name, last_name, role, tenant=None, is_staff=False):
        User = get_user_model()

        defaults = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "is_active": True,
            "is_staff": is_staff,
        }

        if self.has_field(User, "tenant"):
            defaults["tenant"] = tenant

        user = User.objects.filter(username=username).first()

        if user:
            for key, value in defaults.items():
                setattr(user, key, value)
            user.set_password(DEMO_PASSWORD)
            user.save()
        else:
            user = User.objects.create_user(
                username=username,
                password=DEMO_PASSWORD,
                **defaults,
            )

        group = Group.objects.get(name=role)
        user.groups.clear()
        user.groups.add(group)

        return user

    # -------------------------------------------------
    # Tenant / school
    # -------------------------------------------------

    def create_tenant(self, Tenant, name, code, email):
        data = {}

        self.set_field(Tenant, data, ["name", "school_name", "tenant_name"], name)
        self.set_field(Tenant, data, ["code", "tenant_code", "school_code"], code)
        self.set_field(Tenant, data, ["email", "contact_email"], email)
        self.set_field(Tenant, data, ["phone", "contact_number"], "07123456789")
        self.set_field(Tenant, data, ["address"], "London, United Kingdom")
        self.set_field(Tenant, data, ["city"], "London")
        self.set_field(Tenant, data, ["country"], "United Kingdom")
        self.set_field(Tenant, data, ["status"], "Active")
        self.set_field(Tenant, data, ["is_active"], True)

        lookup = {}
        if self.has_field(Tenant, "name"):
            lookup["name"] = name
        elif self.has_field(Tenant, "school_name"):
            lookup["school_name"] = name
        elif self.has_field(Tenant, "tenant_name"):
            lookup["tenant_name"] = name
        else:
            lookup = data

        return self.create_or_update(Tenant, lookup=lookup, defaults=data)

    # -------------------------------------------------
    # Main school demo dataset
    # -------------------------------------------------

    def create_school_dataset(self, tenant, prefix, school_short_name, admin_name):
        school_admin = self.create_user(
            username=f"{prefix}_admin",
            email=f"{prefix}_admin@example.com",
            first_name=admin_name[0],
            last_name=admin_name[1],
            role="School Admin",
            tenant=tenant,
            is_staff=True,
        )

        accountant = self.create_user(
            username=f"{prefix}_accountant",
            email=f"{prefix}_accountant@example.com",
            first_name="Riya",
            last_name="Mehta",
            role="Accountant",
            tenant=tenant,
        )

        librarian = self.create_user(
            username=f"{prefix}_librarian",
            email=f"{prefix}_librarian@example.com",
            first_name="Neha",
            last_name="Kapoor",
            role="Librarian",
            tenant=tenant,
        )

        academic_year = self.create_academic_year(tenant, school_short_name)
        academic_term = self.create_academic_term(academic_year, school_short_name)

        classes = self.create_classes(tenant, school_short_name)
        sections = self.create_sections(tenant, classes, school_short_name)
        subjects = self.create_subjects(tenant, school_short_name)

        teachers = self.create_teachers(tenant, prefix, subjects)
        students = self.create_students(tenant, prefix, classes, sections)

        assignments = self.create_teacher_subjects(
            teachers=teachers,
            subjects=subjects,
            classes=classes,
            sections=sections,
            academic_year=academic_year,
        )

        self.create_timetables(tenant, academic_term, assignments)
        self.create_attendance(tenant, students, teachers, school_admin)
        examinations = self.create_examinations(tenant, academic_term, classes, subjects)
        self.create_marks_and_results(tenant, students, examinations, academic_term, teachers)
        self.create_fees(tenant, academic_term, classes, students, accountant)
        self.create_library(tenant, students, librarian)
        self.create_announcements(tenant, school_admin)

    # -------------------------------------------------
    # Academic data
    # -------------------------------------------------

    def create_academic_year(self, tenant, school_short_name):
        AcademicYear = self.get_model("core", "AcademicYear")
        if AcademicYear is None:
            return None

        year_name = f"{school_short_name} 2026-2027"

        data = {}
        self.set_field(AcademicYear, data, ["tenant"], tenant)
        self.set_field(AcademicYear, data, ["year_name", "name", "academic_year"], year_name)
        self.set_field(AcademicYear, data, ["start_date"], date(2026, 9, 1))
        self.set_field(AcademicYear, data, ["end_date"], date(2027, 7, 31))
        self.set_field(AcademicYear, data, ["is_current"], True)

        lookup = {}
        if self.has_field(AcademicYear, "year_name"):
            lookup["year_name"] = year_name
        elif self.has_field(AcademicYear, "name"):
            lookup["name"] = year_name
        else:
            lookup = data

        if self.has_field(AcademicYear, "tenant"):
            lookup["tenant"] = tenant

        return self.create_or_update(AcademicYear, lookup=lookup, defaults=data)

    def create_academic_term(self, academic_year, school_short_name):
        AcademicTerm = self.get_model("core", "AcademicTerm")
        if AcademicTerm is None or academic_year is None:
            return None

        term_name = f"{school_short_name} Term 1"

        data = {}
        self.set_field(AcademicTerm, data, ["academic_year"], academic_year)
        self.set_field(AcademicTerm, data, ["term_name", "name"], term_name)
        self.set_field(AcademicTerm, data, ["start_date"], date(2026, 9, 1))
        self.set_field(AcademicTerm, data, ["end_date"], date(2026, 12, 20))
        self.set_field(AcademicTerm, data, ["is_current"], True)

        lookup = {}
        if self.has_field(AcademicTerm, "academic_year"):
            lookup["academic_year"] = academic_year
        if self.has_field(AcademicTerm, "term_name"):
            lookup["term_name"] = term_name
        elif self.has_field(AcademicTerm, "name"):
            lookup["name"] = term_name

        return self.create_or_update(AcademicTerm, lookup=lookup, defaults=data)

    def create_classes(self, tenant, school_short_name):
        SchoolClass = self.get_model("core", "SchoolClass")
        if SchoolClass is None:
            return []

        classes = []
        for year in ["Year 7", "Year 8", "Year 9"]:
            class_name = f"{school_short_name} {year}"

            data = {}
            self.set_field(SchoolClass, data, ["tenant"], tenant)
            self.set_field(SchoolClass, data, ["class_name", "name"], class_name)
            self.set_field(SchoolClass, data, ["description"], f"Demo class for {class_name}")
            self.set_field(SchoolClass, data, ["is_active"], True)

            lookup = {}
            if self.has_field(SchoolClass, "tenant"):
                lookup["tenant"] = tenant
            if self.has_field(SchoolClass, "class_name"):
                lookup["class_name"] = class_name
            elif self.has_field(SchoolClass, "name"):
                lookup["name"] = class_name

            classes.append(self.create_or_update(SchoolClass, lookup=lookup, defaults=data))

        return classes

    def create_sections(self, tenant, classes, school_short_name):
        Section = self.get_model("core", "Section")
        if Section is None:
            return []

        sections = []
        for school_class in classes:
            for sec in ["A", "B"]:
                section_name = f"{school_short_name}-{sec}"

                data = {}
                self.set_field(Section, data, ["tenant"], tenant)
                self.set_field(Section, data, ["school_class", "class_obj"], school_class)
                self.set_field(Section, data, ["section_name", "name"], section_name)
                self.set_field(Section, data, ["is_active"], True)

                lookup = {}
                if self.has_field(Section, "school_class"):
                    lookup["school_class"] = school_class
                if self.has_field(Section, "section_name"):
                    lookup["section_name"] = section_name
                elif self.has_field(Section, "name"):
                    lookup["name"] = section_name

                sections.append(self.create_or_update(Section, lookup=lookup, defaults=data))

        return sections

    def create_subjects(self, tenant, school_short_name):
        Subject = self.get_model("core", "Subject")
        if Subject is None:
            return []

        subject_names = ["Mathematics", "English", "Science", "Computer Science"]
        subjects = []

        for subject_name in subject_names:
            final_name = f"{school_short_name} {subject_name}"

            data = {}
            self.set_field(Subject, data, ["tenant"], tenant)
            self.set_field(Subject, data, ["subject_name", "name"], final_name)
            self.set_field(Subject, data, ["subject_code", "code"], final_name.replace(" ", "_").upper()[:20])
            self.set_field(Subject, data, ["description"], f"Demo subject: {final_name}")
            self.set_field(Subject, data, ["is_active"], True)

            lookup = {}
            if self.has_field(Subject, "tenant"):
                lookup["tenant"] = tenant
            if self.has_field(Subject, "subject_name"):
                lookup["subject_name"] = final_name
            elif self.has_field(Subject, "name"):
                lookup["name"] = final_name

            subjects.append(self.create_or_update(Subject, lookup=lookup, defaults=data))

        return subjects

    # -------------------------------------------------
    # Teachers and students
    # -------------------------------------------------

    def create_teachers(self, tenant, prefix, subjects):
        Teacher = self.get_model("core", "Teacher")
        if Teacher is None:
            return []

        teacher_data = [
            ("Anita", "Desai", "MSc Mathematics"),
            ("Rahul", "Verma", "MA English"),
            ("Meera", "Joshi", "MSc Science"),
            ("Daniel", "Smith", "MSc Computer Science"),
        ]

        teachers = []

        for index, item in enumerate(teacher_data, start=1):
            first_name, last_name, qualification = item
            subject = subjects[index - 1] if index - 1 < len(subjects) else None

            user = self.create_user(
                username=f"{prefix}_teacher{index}",
                email=f"{prefix}_teacher{index}@example.com",
                first_name=first_name,
                last_name=last_name,
                role="Teacher",
                tenant=tenant,
            )

            data = {}
            self.set_field(Teacher, data, ["tenant"], tenant)
            self.set_field(Teacher, data, ["user"], user)
            self.set_field(Teacher, data, ["teacher_id"], f"{prefix.upper()}T{index:03d}")
            self.set_field(Teacher, data, ["employee_number"], f"{prefix.upper()}EMP{index:03d}")
            self.set_field(Teacher, data, ["first_name"], first_name)
            self.set_field(Teacher, data, ["last_name"], last_name)
            self.set_field(Teacher, data, ["email"], f"{prefix}_teacher{index}@example.com")
            self.set_field(Teacher, data, ["phone"], f"07123456{index:03d}")
            self.set_field(Teacher, data, ["qualification"], qualification)
            self.set_field(Teacher, data, ["hire_date"], date(2024, 9, 1))
            self.set_field(Teacher, data, ["is_active"], True)

            if subject is not None:
                subject_name = str(subject)
                self.set_field(Teacher, data, ["subject"], subject_name[:100])

            lookup = {}
            if self.has_field(Teacher, "teacher_id"):
                lookup["teacher_id"] = f"{prefix.upper()}T{index:03d}"
            elif self.has_field(Teacher, "email"):
                lookup["email"] = f"{prefix}_teacher{index}@example.com"

            teachers.append(self.create_or_update(Teacher, lookup=lookup, defaults=data))

        return teachers

    def create_students(self, tenant, prefix, classes, sections):
        Student = self.get_model("core", "Student")
        if Student is None:
            return []

        student_names = [
            ("Aisha", "Khan", "Female"),
            ("Rohan", "Patel", "Male"),
            ("Emily", "Brown", "Female"),
            ("Kabir", "Shah", "Male"),
            ("Sofia", "Wilson", "Female"),
            ("Arjun", "Mehta", "Male"),
            ("Olivia", "Taylor", "Female"),
            ("Dev", "Joshi", "Male"),
        ]

        if not self.quick:
            student_names += [
                ("Maya", "Kapoor", "Female"),
                ("Harry", "Clark", "Male"),
                ("Isha", "Desai", "Female"),
                ("Noah", "Evans", "Male"),
            ]

        students = []

        for index, item in enumerate(student_names, start=1):
            first_name, last_name, gender = item

            school_class = classes[index % len(classes)] if classes else None
            section = sections[index % len(sections)] if sections else None

            user = self.create_user(
                username=f"{prefix}_student{index}",
                email=f"{prefix}_student{index}@example.com",
                first_name=first_name,
                last_name=last_name,
                role="Student",
                tenant=tenant,
            )

            data = {}
            self.set_field(Student, data, ["tenant"], tenant)
            self.set_field(Student, data, ["user"], user)
            self.set_field(Student, data, ["student_id"], f"{prefix.upper()}S{index:03d}")
            self.set_field(Student, data, ["admission_number"], f"{prefix.upper()}ADM{index:03d}")
            self.set_field(Student, data, ["first_name"], first_name)
            self.set_field(Student, data, ["last_name"], last_name)
            self.set_field(Student, data, ["email"], f"{prefix}_student{index}@example.com")
            self.set_field(Student, data, ["phone"], f"07987654{index:03d}")
            self.set_field(Student, data, ["date_of_birth"], date(2012, 1, 1) + timedelta(days=index * 40))
            self.set_field(Student, data, ["gender"], gender)
            self.set_field(Student, data, ["address"], "London, United Kingdom")
            self.set_field(Student, data, ["admission_date"], date(2026, 9, 1))
            self.set_field(Student, data, ["is_active"], True)
            self.set_field(Student, data, ["school_class"], school_class)
            self.set_field(Student, data, ["section"], section)

            lookup = {}
            if self.has_field(Student, "student_id"):
                lookup["student_id"] = f"{prefix.upper()}S{index:03d}"
            elif self.has_field(Student, "email"):
                lookup["email"] = f"{prefix}_student{index}@example.com"

            students.append(self.create_or_update(Student, lookup=lookup, defaults=data))

        return students

    # -------------------------------------------------
    # Teacher assignments and timetable
    # -------------------------------------------------

    def create_teacher_subjects(self, teachers, subjects, classes, sections, academic_year):
        TeacherSubject = self.get_model("core", "TeacherSubject")
        if TeacherSubject is None:
            return []

        assignments = []

        for index, teacher in enumerate(teachers):
            subject = subjects[index % len(subjects)] if subjects else None
            school_class = classes[index % len(classes)] if classes else None
            section = sections[index % len(sections)] if sections else None

            data = {}
            self.set_field(TeacherSubject, data, ["teacher"], teacher)
            self.set_field(TeacherSubject, data, ["subject"], subject)
            self.set_field(TeacherSubject, data, ["school_class"], school_class)
            self.set_field(TeacherSubject, data, ["section"], section)
            self.set_field(TeacherSubject, data, ["academic_year"], academic_year)
            self.set_field(TeacherSubject, data, ["is_active"], True)

            lookup = {}
            for field_name in ["teacher", "subject", "school_class", "section", "academic_year"]:
                if self.has_field(TeacherSubject, field_name) and field_name in data:
                    lookup[field_name] = data[field_name]

            assignments.append(self.create_or_update(TeacherSubject, lookup=lookup, defaults=data))

        return assignments

    def create_timetables(self, tenant, academic_term, assignments):
        Timetable = self.get_model("core", "Timetable")
        if Timetable is None or academic_term is None:
            return []

        created = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday"]

        for index, assignment in enumerate(assignments):
            day = days[index % len(days)]

            data = {}
            self.set_field(Timetable, data, ["tenant"], tenant)
            self.set_field(Timetable, data, ["academic_term"], academic_term)
            self.set_field(Timetable, data, ["teacher_assignment"], assignment)
            self.set_field(Timetable, data, ["day"], day)
            self.set_field(Timetable, data, ["start_time"], time(9 + index, 0))
            self.set_field(Timetable, data, ["end_time"], time(10 + index, 0))
            self.set_field(Timetable, data, ["room_number", "room"], f"R{101 + index}")

            lookup = {}
            for field_name in ["academic_term", "teacher_assignment", "day", "start_time"]:
                if self.has_field(Timetable, field_name) and field_name in data:
                    lookup[field_name] = data[field_name]

            created.append(self.create_or_update(Timetable, lookup=lookup, defaults=data))

        return created

    # -------------------------------------------------
    # Attendance
    # -------------------------------------------------

    def create_attendance(self, tenant, students, teachers, recorded_by):
        StudentAttendance = self.get_model("core", "StudentAttendance")
        StaffAttendance = self.get_model("core", "StaffAttendance")

        today = date.today()

        if StudentAttendance is not None:
            for student in students:
                for day_offset in range(3):
                    attendance_date = today - timedelta(days=day_offset)
                    status = "Present" if day_offset != 1 else "Absent"

                    data = {}
                    self.set_field(StudentAttendance, data, ["tenant"], tenant)
                    self.set_field(StudentAttendance, data, ["student"], student)
                    self.set_field(StudentAttendance, data, ["date", "attendance_date"], attendance_date)
                    self.set_field(StudentAttendance, data, ["status"], status)
                    self.set_field(StudentAttendance, data, ["remarks"], "Demo attendance record")
                    self.set_field(StudentAttendance, data, ["recorded_by", "created_by"], recorded_by)

                    lookup = {}
                    for field_name in ["student", "date", "attendance_date"]:
                        if self.has_field(StudentAttendance, field_name) and field_name in data:
                            lookup[field_name] = data[field_name]

                    self.create_or_update(StudentAttendance, lookup=lookup, defaults=data)

        if StaffAttendance is not None:
            for teacher in teachers:
                for day_offset in range(3):
                    attendance_date = today - timedelta(days=day_offset)
                    status = "Present"

                    data = {}
                    self.set_field(StaffAttendance, data, ["tenant"], tenant)
                    self.set_field(StaffAttendance, data, ["teacher", "staff"], teacher)
                    self.set_field(StaffAttendance, data, ["date", "attendance_date"], attendance_date)
                    self.set_field(StaffAttendance, data, ["status"], status)
                    self.set_field(StaffAttendance, data, ["remarks"], "Demo staff attendance")
                    self.set_field(StaffAttendance, data, ["recorded_by", "created_by"], recorded_by)

                    lookup = {}
                    for field_name in ["teacher", "staff", "date", "attendance_date"]:
                        if self.has_field(StaffAttendance, field_name) and field_name in data:
                            lookup[field_name] = data[field_name]

                    self.create_or_update(StaffAttendance, lookup=lookup, defaults=data)

    # -------------------------------------------------
    # Exams, marks and results
    # -------------------------------------------------

    def create_examinations(self, tenant, academic_term, classes, subjects):
        Examination = self.get_model("core", "Examination")
        if Examination is None or academic_term is None:
            return []

        examinations = []

        for index, subject in enumerate(subjects):
            school_class = classes[index % len(classes)] if classes else None

            data = {}
            self.set_field(Examination, data, ["tenant"], tenant)
            self.set_field(Examination, data, ["academic_term"], academic_term)
            self.set_field(Examination, data, ["school_class"], school_class)
            self.set_field(Examination, data, ["subject"], subject)
            self.set_field(Examination, data, ["exam_type"], "Mid Term")
            self.set_field(Examination, data, ["exam_date"], date.today() + timedelta(days=10 + index))
            self.set_field(Examination, data, ["start_time"], time(10, 0))
            self.set_field(Examination, data, ["end_time"], time(12, 0))
            self.set_field(Examination, data, ["total_marks"], 100)
            self.set_field(Examination, data, ["passing_marks"], 35)
            self.set_field(Examination, data, ["instructions"], "Demo examination instructions.")
            self.set_field(Examination, data, ["is_published"], True)

            lookup = {}
            for field_name in ["academic_term", "school_class", "subject", "exam_type"]:
                if self.has_field(Examination, field_name) and field_name in data:
                    lookup[field_name] = data[field_name]

            examinations.append(self.create_or_update(Examination, lookup=lookup, defaults=data))

        return examinations

    def create_marks_and_results(self, tenant, students, examinations, academic_term, teachers):
        StudentMark = self.get_model("core", "StudentMark")
        Result = self.get_model("core", "Result")

        entered_by = teachers[0] if teachers else None
        if StudentMark is not None:
            for s_index, student in enumerate(students, start=1):
                for e_index, examination in enumerate(examinations, start=1):
                    mark = 55 + ((s_index + e_index) % 40)

                    data = {}
                    self.set_field(StudentMark, data, ["tenant"], tenant)
                    self.set_field(StudentMark, data, ["student"], student)
                    self.set_field(StudentMark, data, ["examination"], examination)
                    self.set_field(StudentMark, data, ["marks_obtained", "marks"], mark)
                    self.set_field(StudentMark, data, ["remarks"], "Good performance")
                    self.set_field(StudentMark, data, ["entered_by", "created_by"], entered_by)

                    lookup = {}
                    for field_name in ["student", "examination"]:
                        if self.has_field(StudentMark, field_name) and field_name in data:
                            lookup[field_name] = data[field_name]

                    self.create_or_update(StudentMark, lookup=lookup, defaults=data)

        if Result is not None and academic_term is not None:
            for s_index, student in enumerate(students, start=1):
                percentage = Decimal(str(60 + (s_index % 30)))
                grade = "A" if percentage >= 75 else "B"

                data = {}
                self.set_field(Result, data, ["tenant"], tenant)
                self.set_field(Result, data, ["student"], student)
                self.set_field(Result, data, ["academic_term"], academic_term)
                self.set_field(Result, data, ["total_marks"], int(percentage * 4))
                self.set_field(Result, data, ["percentage"], percentage)
                self.set_field(Result, data, ["grade"], grade)
                self.set_field(Result, data, ["result_status", "status"], "PASS")
                self.set_field(Result, data, ["is_published"], True)

                lookup = {}
                for field_name in ["student", "academic_term"]:
                    if self.has_field(Result, field_name) and field_name in data:
                        lookup[field_name] = data[field_name]

                self.create_or_update(Result, lookup=lookup, defaults=data)

    # -------------------------------------------------
    # Fees
    # -------------------------------------------------

    def create_fees(self, tenant, academic_term, classes, students, accountant):
        FeeStructure = self.get_model("core", "FeeStructure")
        StudentFee = self.get_model("core", "StudentFee")
        FeePayment = self.get_model("core", "FeePayment")

        fee_structures = []

        if FeeStructure is not None:
            fee_types = [
                ("Tuition Fee", Decimal("1200.00")),
                ("Exam Fee", Decimal("150.00")),
                ("Library Fee", Decimal("80.00")),
            ]

            for fee_type, amount in fee_types:
                school_class = classes[0] if classes else None

                data = {}
                self.set_field(FeeStructure, data, ["tenant"], tenant)
                self.set_field(FeeStructure, data, ["academic_term"], academic_term)
                self.set_field(FeeStructure, data, ["school_class"], school_class)
                self.set_field(FeeStructure, data, ["fee_type", "name", "title"], fee_type)
                self.set_field(FeeStructure, data, ["amount"], amount)
                self.set_field(FeeStructure, data, ["due_date"], date.today() + timedelta(days=30))
                self.set_field(FeeStructure, data, ["description"], f"Demo {fee_type}")
                self.set_field(FeeStructure, data, ["is_active"], True)

                lookup = {}
                for field_name in ["tenant", "academic_term", "school_class", "fee_type", "name"]:
                    if self.has_field(FeeStructure, field_name) and field_name in data:
                        lookup[field_name] = data[field_name]

                fee_structures.append(self.create_or_update(FeeStructure, lookup=lookup, defaults=data))

        if StudentFee is not None and fee_structures:
            for student in students:
                fee_structure = fee_structures[0]

                data = {}
                self.set_field(StudentFee, data, ["tenant"], tenant)
                self.set_field(StudentFee, data, ["student"], student)
                self.set_field(StudentFee, data, ["fee_structure"], fee_structure)
                self.set_field(StudentFee, data, ["academic_term"], academic_term)
                self.set_field(StudentFee, data, ["total_amount", "amount"], Decimal("1200.00"))
                self.set_field(StudentFee, data, ["amount_paid", "paid_amount"], Decimal("600.00"))
                self.set_field(StudentFee, data, ["balance_amount", "remaining_amount"], Decimal("600.00"))
                self.set_field(StudentFee, data, ["due_date"], date.today() + timedelta(days=30))
                self.set_field(StudentFee, data, ["status"], "Partially Paid")

                lookup = {}
                for field_name in ["student", "fee_structure", "academic_term"]:
                    if self.has_field(StudentFee, field_name) and field_name in data:
                        lookup[field_name] = data[field_name]

                student_fee = self.create_or_update(StudentFee, lookup=lookup, defaults=data)

                if FeePayment is not None:
                    payment_data = {}
                    self.set_field(FeePayment, payment_data, ["tenant"], tenant)
                    self.set_field(FeePayment, payment_data, ["student_fee"], student_fee)
                    self.set_field(FeePayment, payment_data, ["amount", "paid_amount"], Decimal("600.00"))
                    self.set_field(FeePayment, payment_data, ["payment_date", "date"], date.today())
                    self.set_field(FeePayment, payment_data, ["payment_method", "method"], "Cash")
                    self.set_field(FeePayment, payment_data, ["transaction_id", "receipt_number"], f"PAY-{student.id}")
                    self.set_field(FeePayment, payment_data, ["received_by", "created_by"], accountant)

                    payment_lookup = {}
                    for field_name in ["student_fee", "transaction_id", "receipt_number"]:
                        if self.has_field(FeePayment, field_name) and field_name in payment_data:
                            payment_lookup[field_name] = payment_data[field_name]

                    self.create_or_update(FeePayment, lookup=payment_lookup, defaults=payment_data)

    # -------------------------------------------------
    # Library
    # -------------------------------------------------

    def create_library(self, tenant, students, librarian):
        BookCategory = self.get_model("core", "BookCategory")
        Book = self.get_model("core", "Book")
        LibraryIssue = self.get_model("core", "LibraryIssue")

        categories = []

        if BookCategory is not None:
            for category_name in ["Fiction", "Science", "Computer Science"]:
                data = {}
                self.set_field(BookCategory, data, ["tenant"], tenant)
                self.set_field(BookCategory, data, ["category_name", "name"], category_name)
                self.set_field(BookCategory, data, ["description"], f"Demo {category_name} books")

                lookup = {}
                if self.has_field(BookCategory, "tenant"):
                    lookup["tenant"] = tenant
                if self.has_field(BookCategory, "category_name"):
                    lookup["category_name"] = category_name
                elif self.has_field(BookCategory, "name"):
                    lookup["name"] = category_name

                categories.append(self.create_or_update(BookCategory, lookup=lookup, defaults=data))

        books = []

        if Book is not None:
            book_items = [
                ("Introduction to Python", "Mark Wilson"),
                ("School Science Companion", "Emma Johnson"),
                ("Mathematics Practice Book", "David Brown"),
                ("English Grammar Guide", "Sarah Taylor"),
            ]

            for index, item in enumerate(book_items, start=1):
                title, author = item
                category = categories[index % len(categories)] if categories else None

                data = {}
                self.set_field(Book, data, ["tenant"], tenant)
                self.set_field(Book, data, ["category"], category)
                self.set_field(Book, data, ["title", "book_name", "name"], title)
                self.set_field(Book, data, ["author"], author)
                self.set_field(Book, data, ["isbn"], f"97800000000{index}")
                self.set_field(Book, data, ["publisher"], "Demo Publisher")
                self.set_field(Book, data, ["published_year", "year"], 2024)
                self.set_field(Book, data, ["total_copies"], 10)
                self.set_field(Book, data, ["available_copies"], 7)
                self.set_field(Book, data, ["is_active"], True)

                lookup = {}
                if self.has_field(Book, "tenant"):
                    lookup["tenant"] = tenant
                if self.has_field(Book, "isbn"):
                    lookup["isbn"] = f"97800000000{index}"
                elif self.has_field(Book, "title"):
                    lookup["title"] = title

                books.append(self.create_or_update(Book, lookup=lookup, defaults=data))

        if LibraryIssue is not None and books and students:
            for index, student in enumerate(students[:5], start=1):
                book = books[index % len(books)]

                data = {}
                self.set_field(LibraryIssue, data, ["tenant"], tenant)
                self.set_field(LibraryIssue, data, ["book"], book)
                self.set_field(LibraryIssue, data, ["student"], student)

                if hasattr(student, "user"):
                    self.set_field(LibraryIssue, data, ["user", "issued_to"], student.user)

                self.set_field(LibraryIssue, data, ["issue_date"], date.today() - timedelta(days=index))
                self.set_field(LibraryIssue, data, ["due_date"], date.today() + timedelta(days=14))
                self.set_field(LibraryIssue, data, ["return_date"], None)
                self.set_field(LibraryIssue, data, ["status"], "Issued")
                self.set_field(LibraryIssue, data, ["fine_amount", "fine"], Decimal("0.00"))
                self.set_field(LibraryIssue, data, ["issued_by", "created_by"], librarian)

                lookup = {}
                for field_name in ["book", "student", "user", "issue_date"]:
                    if self.has_field(LibraryIssue, field_name) and field_name in data:
                        lookup[field_name] = data[field_name]

                self.create_or_update(LibraryIssue, lookup=lookup, defaults=data)

    # -------------------------------------------------
    # Announcements
    # -------------------------------------------------

    def create_announcements(self, tenant, created_by):
        Announcement = self.get_model("core", "Announcement")
        if Announcement is None:
            return

        announcements = [
            ("Welcome to the New Academic Year", "The new academic year has started successfully.", "All", "Normal"),
            ("Mid Term Examination Notice", "Mid term examinations will begin next week.", "Student", "High"),
            ("Staff Meeting Reminder", "All staff members are requested to attend the meeting.", "Teacher", "Normal"),
        ]

        for title, message, target_role, priority in announcements:
            data = {}
            self.set_field(Announcement, data, ["tenant"], tenant)
            self.set_field(Announcement, data, ["title"], title)
            self.set_field(Announcement, data, ["message", "description"], message)
            self.set_field(Announcement, data, ["target_role", "role"], target_role)
            self.set_field(Announcement, data, ["priority"], priority)
            self.set_field(Announcement, data, ["start_date"], date.today())
            self.set_field(Announcement, data, ["end_date"], date.today() + timedelta(days=30))
            self.set_field(Announcement, data, ["is_active"], True)
            self.set_field(Announcement, data, ["created_by"], created_by)

            lookup = {}
            if self.has_field(Announcement, "tenant"):
                lookup["tenant"] = tenant
            if self.has_field(Announcement, "title"):
                lookup["title"] = title

            self.create_or_update(Announcement, lookup=lookup, defaults=data)

    # -------------------------------------------------
    # Fallback for any empty core models
    # -------------------------------------------------

    def seed_remaining_empty_core_models(self):
        for model in apps.get_models():
            if model._meta.app_label != "core":
                continue

            if model.objects.exists():
                continue

            try:
                data = {}
                self.complete_required_fields(model, data)

                if data:
                    model.objects.create(**data)
                    self.stdout.write(self.style.WARNING(f"Created basic demo row for {model.__name__}"))
            except Exception as error:
                self.stdout.write(self.style.WARNING(f"Skipped {model.__name__}: {error}"))