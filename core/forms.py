from django import forms
from tenants.models import Tenant
from .models import AcademicYear, AcademicTerm, SchoolClass, Section, Subject, Teacher, TeacherSubject, Student, StaffAttendance, Timetable, Examination, ExamHallAllocation, StudentMark, Result, FeePayment, FeeStructure, StudentFee, BookCategory, Book, LibraryIssue, Announcement, AcademicTerm, AcademicYear
from django.db.models import Q

class AcademicYearForm(forms.ModelForm):

    class Meta:
        model = AcademicYear

        fields = [
            "tenant",
            "year_name",
            "start_date",
            "end_date",
            "is_current",
        ]

        widgets = {
            "year_name": forms.TextInput(
                attrs={
                    "placeholder": "Example: 2026-2027",
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user:
            is_product_owner = current_user.groups.filter(
                name="Product Owner"
            ).exists()

            if not is_product_owner:
                self.fields["tenant"].initial = current_user.tenant
                self.fields["tenant"].disabled = True

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError(
                    "End date must be after the start date."
                )

        return cleaned_data

    def save(self, commit=True):
        academic_year = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            academic_year.tenant = self.current_user.tenant

        if commit:
            if academic_year.is_current:
                AcademicYear.objects.filter(
                    tenant=academic_year.tenant,
                    is_current=True,
                ).exclude(
                    pk=academic_year.pk
                ).update(
                    is_current=False
                )

            academic_year.save()

        return academic_year

class AcademicTermForm(forms.ModelForm):

    class Meta:
        model = AcademicTerm

        fields = [
            "academic_year",
            "term_name",
            "start_date",
            "end_date",
            "is_current",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, current_user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        for field_name, field in self.fields.items():

            field.widget.attrs.update(
                {
                    "class": "form-control",
                }
            )

        if current_user and current_user.groups.filter(name="School Admin").exists():

            self.fields["academic_year"].queryset = AcademicYear.objects.filter(
                tenant=current_user.tenant
            )

    def clean(self):

        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:

            raise forms.ValidationError(
                "End date cannot be before start date."
            )

        return cleaned_data

    def save(self, commit=True):

        academic_term = super().save(commit=False)

        if commit:

            academic_term.save()

            if academic_term.is_current:

                AcademicTerm.objects.filter(
                    academic_year=academic_term.academic_year,
                    is_current=True,
                ).exclude(
                    id=academic_term.id
                ).update(
                    is_current=False
                )

        return academic_term
class SchoolClassForm(forms.ModelForm):

    class Meta:
        model = SchoolClass

        fields = [
            "tenant",
            "academic_year",
            "class_name",
        ]

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:
            self.fields["tenant"].queryset = Tenant.objects.all()

            self.fields["academic_year"].queryset = (
                AcademicYear.objects.all()
            )

        else:
            self.fields["tenant"].queryset = Tenant.objects.filter(
                id=current_user.tenant_id
            )

            self.fields["tenant"].initial = current_user.tenant
            self.fields["tenant"].disabled = True

            self.fields["academic_year"].queryset = (
                AcademicYear.objects.filter(
                    tenant=current_user.tenant
                )
            )

    def clean(self):
        cleaned_data = super().clean()

        tenant = cleaned_data.get("tenant")
        academic_year = cleaned_data.get("academic_year")

        if tenant and academic_year:
            if academic_year.tenant_id != tenant.id:
                raise forms.ValidationError(
                    "The academic year must belong to the selected tenant."
                )

        return cleaned_data

    def save(self, commit=True):
        school_class = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            school_class.tenant = self.current_user.tenant

        if commit:
            school_class.save()

        return school_class

class SectionForm(forms.ModelForm):

    class Meta:
        model = Section

        fields = [
            "school_class",
            "section_name",
        ]

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:
            self.fields["school_class"].queryset = (
                SchoolClass.objects.all()
            )
        else:
            self.fields["school_class"].queryset = (
                SchoolClass.objects.filter(
                    tenant=current_user.tenant
                )
            )

class SubjectForm(forms.ModelForm):

    class Meta:
        model = Subject

        fields = [
            "tenant",
            "subject_name",
            "subject_code",
        ]

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if not is_product_owner:
            self.fields["tenant"].initial = current_user.tenant
            self.fields["tenant"].disabled = True

    def save(self, commit=True):
        subject = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            subject.tenant = self.current_user.tenant

        if commit:
            subject.save()

        return subject

class TeacherSubjectForm(forms.ModelForm):

    class Meta:
        model = TeacherSubject

        fields = [
            "teacher",
            "subject",
            "school_class",
            "section",
            "academic_year",
        ]

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if not is_product_owner:
            tenant = current_user.tenant

            self.fields["teacher"].queryset = Teacher.objects.filter(
                tenant=tenant
            )

            self.fields["subject"].queryset = Subject.objects.filter(
                tenant=tenant
            )

            self.fields["school_class"].queryset = SchoolClass.objects.filter(
                tenant=tenant
            )

            self.fields["section"].queryset = Section.objects.filter(
                school_class__tenant=tenant
            )

            self.fields["academic_year"].queryset = AcademicYear.objects.filter(
                tenant=tenant
            )

    def clean(self):
        cleaned_data = super().clean()

        teacher = cleaned_data.get("teacher")
        subject = cleaned_data.get("subject")
        school_class = cleaned_data.get("school_class")
        section = cleaned_data.get("section")
        academic_year = cleaned_data.get("academic_year")

        if not all([
            teacher,
            subject,
            school_class,
            section,
            academic_year,
        ]):
            return cleaned_data

        tenant_id = school_class.tenant_id

        if teacher.tenant_id != tenant_id:
            raise forms.ValidationError(
                "Teacher and class must belong to the same tenant."
            )

        if subject.tenant_id != tenant_id:
            raise forms.ValidationError(
                "Subject and class must belong to the same tenant."
            )

        if academic_year.tenant_id != tenant_id:
            raise forms.ValidationError(
                "Academic year must belong to the same tenant."
            )

        if section.school_class_id != school_class.id:
            raise forms.ValidationError(
                "Section must belong to the selected class."
            )

        if school_class.academic_year_id != academic_year.id:
            raise forms.ValidationError(
                "Class must belong to the selected academic year."
            )

        return cleaned_data
class StudentForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
            "tenant",
            "user",
            "admission_number",
            "student_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "gender",
            "address",
            "admission_date",
            "school_class",
            "section",
            "is_active",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date"}
            ),

            "admission_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if not is_product_owner:
            tenant = current_user.tenant

            self.fields["tenant"].initial = tenant
            self.fields["tenant"].disabled = True

            self.fields["school_class"].queryset = (
                SchoolClass.objects.filter(
                    tenant=tenant
                )
            )

            self.fields["section"].queryset = (
                Section.objects.filter(
                    school_class__tenant=tenant
                )
            )

            self.fields["user"].queryset = (
                self.fields["user"].queryset.filter(
                    tenant=tenant
                )
            )

    def clean(self):
        cleaned_data = super().clean()

        tenant = cleaned_data.get("tenant")
        school_class = cleaned_data.get("school_class")
        section = cleaned_data.get("section")

        if school_class and tenant:
            if school_class.tenant_id != tenant.id:
                raise forms.ValidationError(
                    "Class must belong to the selected tenant."
                )

        if section and school_class:
            if section.school_class_id != school_class.id:
                raise forms.ValidationError(
                    "Section must belong to the selected class."
                )

        return cleaned_data

    def save(self, commit=True):
        student = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            student.tenant = self.current_user.tenant

        if commit:
            student.save()

        return student

class TeacherForm(forms.ModelForm):

    class Meta:
        model = Teacher

        fields = [
            "tenant",
            "user",
            "employee_number",
            "teacher_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "qualification",
            "hire_date",
            "subject",
            "is_active",
        ]

        widgets = {
            "hire_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if not is_product_owner:
            self.fields["tenant"].initial = current_user.tenant
            self.fields["tenant"].disabled = True

            self.fields["user"].queryset = (
                self.fields["user"].queryset.filter(
                    tenant=current_user.tenant
                )
            )

    def save(self, commit=True):
        teacher = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            teacher.tenant = self.current_user.tenant

        if commit:
            teacher.save()

        return teacher
class StaffAttendanceForm(forms.ModelForm):

    class Meta:
        model = StaffAttendance

        fields = [
            "attendance_date",
        ]

        widgets = {
            "attendance_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }
class TimetableForm(forms.ModelForm):

    class Meta:
        model = Timetable

        fields = [
            "tenant",
            "academic_term",
            "teacher_assignment",
            "day",
            "start_time",
            "end_time",
            "room_number",
        ]

        widgets = {

            "start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),

            "end_time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),

        }

    def __init__(self, *args, current_user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:

            self.fields["teacher_assignment"].queryset = (
                TeacherSubject.objects.all()
            )

        else:

            tenant = current_user.tenant
            self.fields["academic_term"].queryset = (
                AcademicTerm.objects.filter(
                    academic_year__tenant=tenant
                )
            )
            self.fields["academic_term"].queryset = (
                AcademicTerm.objects.all()
            )
            self.fields["tenant"].initial = tenant
            self.fields["tenant"].disabled = True

            self.fields["teacher_assignment"].queryset = (
                TeacherSubject.objects.filter(
                    teacher__tenant=tenant
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        teacher_assignment = cleaned_data.get(
            "teacher_assignment"
        )

        academic_term = cleaned_data.get(
            "academic_term"
        )

        day = cleaned_data.get(
            "day"
        )

        start_time = cleaned_data.get(
            "start_time"
        )

        end_time = cleaned_data.get(
            "end_time"
        )

        room_number = cleaned_data.get(
            "room_number"
        )

        if (
            start_time
            and end_time
            and end_time <= start_time
        ):

            raise forms.ValidationError(
                "End time must be after the start time."
            )

        if not all([
            teacher_assignment,
            academic_term,
            day,
            start_time,
            end_time,
            room_number,
        ]):
            return cleaned_data

        if (
            teacher_assignment.academic_year
            != academic_term.academic_year
        ):

            raise forms.ValidationError(
                "The selected Teacher Assignment and Academic Term must belong to the same Academic Year."
            )

        # -----------------------------
        # Teacher Conflict
        # -----------------------------

        teacher_conflict = Timetable.objects.filter(
            teacher_assignment__teacher=teacher_assignment.teacher,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if self.instance.pk:
            teacher_conflict = teacher_conflict.exclude(
                pk=self.instance.pk
            )

        if teacher_conflict.exists():

            conflict = teacher_conflict.first()

            raise forms.ValidationError(
                f"Scheduling conflict: "
                f"{teacher_assignment.teacher.first_name} "
                f"{teacher_assignment.teacher.last_name} "
                f"is already assigned to another class on "
                f"{conflict.day} from "
                f"{conflict.start_time.strftime('%H:%M')} "
                f"to "
                f"{conflict.end_time.strftime('%H:%M')}."
            )

        # -----------------------------
        # Class Conflict
        # -----------------------------

        class_conflict = Timetable.objects.filter(
            teacher_assignment__school_class=teacher_assignment.school_class,
            teacher_assignment__section=teacher_assignment.section,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if self.instance.pk:
            class_conflict = class_conflict.exclude(
                pk=self.instance.pk
            )

        if class_conflict.exists():

            conflict = class_conflict.first()

            raise forms.ValidationError(
                f"Unable to save timetable: "
                f"{teacher_assignment.school_class.class_name} - "
                f"{teacher_assignment.section.section_name} "
                f"already has "
                f"{conflict.teacher_assignment.subject.subject_name} "
                f"scheduled from "
                f"{conflict.start_time.strftime('%H:%M')} "
                f"to "
                f"{conflict.end_time.strftime('%H:%M')}."
            )

        # -----------------------------
        # Room Conflict
        # -----------------------------

        room_conflict = Timetable.objects.filter(
            tenant=teacher_assignment.teacher.tenant,
            room_number=room_number,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if self.instance.pk:
            room_conflict = room_conflict.exclude(
                pk=self.instance.pk
            )

        if room_conflict.exists():

            conflict = room_conflict.first()

            raise forms.ValidationError(
                f"Unable to save timetable: "
                f"Room {conflict.room_number} "
                f"is already booked on "
                f"{conflict.day} from "
                f"{conflict.start_time.strftime('%H:%M')} "
                f"to "
                f"{conflict.end_time.strftime('%H:%M')}."
            )

        return cleaned_data

    def save(self, commit=True):

        timetable = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            timetable.tenant = self.current_user.tenant

        if commit:
            timetable.save()

        return timetable
class ExaminationForm(forms.ModelForm):

    class Meta:

        model = Examination

        fields = [
            "tenant",
            "academic_term",
            "school_class",
            "subject",
            "exam_type",
            "exam_date",
            "start_time",
            "end_time",
            "total_marks",
            "passing_marks",
            "instructions",
            "is_published",
        ]

        widgets = {

            "exam_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),

            "end_time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),

            "instructions": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),

        }

    def __init__(self, *args, current_user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:

            self.fields["academic_term"].queryset = AcademicTerm.objects.all()

            self.fields["school_class"].queryset = SchoolClass.objects.all()

            self.fields["subject"].queryset = Subject.objects.all()

        else:

            tenant = current_user.tenant

            self.fields["tenant"].initial = tenant
            self.fields["tenant"].disabled = True

            self.fields["academic_term"].queryset = (
                AcademicTerm.objects.filter(
                    academic_year__tenant=tenant
                )
            )

            self.fields["school_class"].queryset = (
                SchoolClass.objects.filter(
                    tenant=tenant
                )
            )

            self.fields["subject"].queryset = (
                Subject.objects.filter(
                    tenant=tenant
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        academic_term = cleaned_data.get(
            "academic_term"
        )

        school_class = cleaned_data.get(
            "school_class"
        )

        subject = cleaned_data.get(
            "subject"
        )

        exam_date = cleaned_data.get(
            "exam_date"
        )

        start_time = cleaned_data.get(
            "start_time"
        )

        end_time = cleaned_data.get(
            "end_time"
        )

        total_marks = cleaned_data.get(
            "total_marks"
        )

        passing_marks = cleaned_data.get(
            "passing_marks"
        )

        if (
            start_time
            and end_time
            and end_time <= start_time
        ):

            raise forms.ValidationError(
                "End time must be after the start time."
            )

        if (
            total_marks
            and passing_marks
            and passing_marks > total_marks
        ):

            raise forms.ValidationError(
                "Passing marks cannot be greater than total marks."
            )

        if (
            school_class
            and academic_term
            and school_class.academic_year != academic_term.academic_year
        ):

            raise forms.ValidationError(
                "The selected class and academic term must belong to the same academic year."
            )

        if (
            exam_date
            and academic_term
        ):

            if (
                exam_date < academic_term.start_date
                or exam_date > academic_term.end_date
            ):

                raise forms.ValidationError(
                    "The examination date must fall within the selected academic term."
                )

        return cleaned_data

    def save(self, commit=True):

        examination = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            examination.tenant = self.current_user.tenant

        if commit:
            examination.save()

        return examination
class ExamHallAllocationForm(forms.ModelForm):

    class Meta:

        model = ExamHallAllocation

        fields = [
            "tenant",
            "section",
            "hall_name",
            "invigilator",
        ]

    def __init__(
        self,
        *args,
        current_user=None,
        examination=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.current_user = current_user
        self.examination = examination

        if current_user is None:
            return

        if current_user.groups.filter(
            name="Product Owner"
        ).exists():

            self.fields["section"].queryset = (
                Section.objects.filter(
                    school_class=examination.school_class
                )
                if examination
                else Section.objects.none()
            )

            self.fields["invigilator"].queryset = (
                Teacher.objects.all()
            )

        else:

            tenant = current_user.tenant

            self.fields["tenant"].initial = tenant
            self.fields["tenant"].disabled = True

            self.fields["section"].queryset = (
                Section.objects.filter(
                    school_class=examination.school_class
                )
                if examination
                else Section.objects.none()
            )

            self.fields["invigilator"].queryset = (
                Teacher.objects.filter(
                    tenant=tenant
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        examination = self.examination

        section = cleaned_data.get("section")
        hall_name = cleaned_data.get("hall_name")
        invigilator = cleaned_data.get("invigilator")

        if not all([
            examination,
            section,
            hall_name,
            invigilator,
        ]):
            return cleaned_data

        if section.school_class != examination.school_class:

            raise forms.ValidationError(
                "The selected section does not belong to this examination."
            )

        hall_conflict = ExamHallAllocation.objects.filter(
            hall_name=hall_name,
            examination__exam_date=examination.exam_date,
            examination__start_time__lt=examination.end_time,
            examination__end_time__gt=examination.start_time,
        )

        if self.instance.pk:
            hall_conflict = hall_conflict.exclude(
                pk=self.instance.pk
            )

        if hall_conflict.exists():

            raise forms.ValidationError(
                "This hall is already allocated during this examination time."
            )

        invigilator_conflict = ExamHallAllocation.objects.filter(
            invigilator=invigilator,
            examination__exam_date=examination.exam_date,
            examination__start_time__lt=examination.end_time,
            examination__end_time__gt=examination.start_time,
        )

        if self.instance.pk:
            invigilator_conflict = invigilator_conflict.exclude(
                pk=self.instance.pk
            )

        if invigilator_conflict.exists():

            raise forms.ValidationError(
                "This invigilator is already supervising another examination during this time."
            )

        return cleaned_data

    def save(self, commit=True):

        allocation = super().save(commit=False)

        allocation.examination = self.examination

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):
            allocation.tenant = self.current_user.tenant

        if commit:
            allocation.save()

        return allocation
class StudentMarkForm(forms.ModelForm):

    class Meta:

        model = StudentMark

        fields = [
            "tenant",
            "examination",
            "student",
            "marks_obtained",
            "remarks",
        ]

    def __init__(
        self,
        *args,
        current_user=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        if current_user.groups.filter(
            name="Product Owner"
        ).exists():

            self.fields["examination"].queryset = (
                Examination.objects.all()
            )

            self.fields["student"].queryset = (
                Student.objects.all()
            )

        else:

            tenant = current_user.tenant

            self.fields["tenant"].initial = tenant
            self.fields["tenant"].disabled = True

            self.fields["examination"].queryset = (
                Examination.objects.filter(
                    tenant=tenant
                )
            )

            self.fields["student"].queryset = (
                Student.objects.filter(
                    tenant=tenant
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        examination = cleaned_data.get(
            "examination"
        )

        student = cleaned_data.get(
            "student"
        )

        marks = cleaned_data.get(
            "marks_obtained"
        )

        if not all([
            examination,
            student,
            marks,
        ]):
            return cleaned_data

        if (
            student.school_class
            != examination.school_class
        ):

            raise forms.ValidationError(
                "Student does not belong to the selected examination class."
            )

        if (
            marks < 0
            or marks > examination.total_marks
        ):

            raise forms.ValidationError(
                f"Marks must be between 0 and {examination.total_marks}."
            )

        return cleaned_data

    def save(self, commit=True):

        student_mark = super().save(
            commit=False
        )

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):

            student_mark.tenant = (
                self.current_user.tenant
            )

            teacher = Teacher.objects.filter(
                user=self.current_user
            ).first()

            student_mark.entered_by = teacher

        if commit:

            student_mark.save()

        return student_mark
class ResultForm(forms.ModelForm):

    class Meta:

        model = Result

        fields = [

            "tenant",

            "student",

            "academic_term",

            "is_published",

        ]

    def __init__(
        self,
        *args,
        current_user=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        if current_user is None:
            return

        if current_user.groups.filter(
            name="Product Owner"
        ).exists():

            self.fields["student"].queryset = (
                Student.objects.all()
            )

            self.fields["academic_term"].queryset = (
                AcademicTerm.objects.all()
            )

        else:

            tenant = current_user.tenant

            self.fields["tenant"].initial = tenant
            self.fields["tenant"].disabled = True

            self.fields["student"].queryset = (
                Student.objects.filter(
                    tenant=tenant
                )
            )

            self.fields["academic_term"].queryset = (
                AcademicTerm.objects.filter(
                    academic_year__tenant=tenant
                )
            )
class FeeStructureForm(forms.ModelForm):

    class Meta:

        model = FeeStructure

        fields = [
            "tenant",
            "academic_term",
            "school_class",
            "fee_name",
            "amount",
            "due_date",
            "is_active",
        ]

        widgets = {
            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def __init__(
        self,
        *args,
        current_user=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:

            self.fields["tenant"].queryset = Tenant.objects.all()

            self.fields["academic_term"].queryset = (
                AcademicTerm.objects.all()
            )

            self.fields["school_class"].queryset = (
                SchoolClass.objects.all()
            )

        else:

            tenant = current_user.tenant

            self.fields["tenant"].initial = tenant
            self.fields["tenant"].disabled = True

            self.fields["academic_term"].queryset = (
                AcademicTerm.objects.filter(
                    academic_year__tenant=tenant
                )
            )

            self.fields["school_class"].queryset = (
                SchoolClass.objects.filter(
                    tenant=tenant
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        tenant = cleaned_data.get(
            "tenant"
        )

        academic_term = cleaned_data.get(
            "academic_term"
        )

        school_class = cleaned_data.get(
            "school_class"
        )

        amount = cleaned_data.get(
            "amount"
        )

        due_date = cleaned_data.get(
            "due_date"
        )

        if amount is not None and amount <= 0:

            raise forms.ValidationError(
                "Fee amount must be greater than zero."
            )

        if not all([
            tenant,
            academic_term,
            school_class,
            due_date,
        ]):
            return cleaned_data

        if academic_term.academic_year.tenant != tenant:

            raise forms.ValidationError(
                "Academic term must belong to the selected tenant."
            )

        if school_class.tenant != tenant:

            raise forms.ValidationError(
                "Class must belong to the selected tenant."
            )

        if school_class.academic_year != academic_term.academic_year:

            raise forms.ValidationError(
                "Class and academic term must belong to the same academic year."
            )

        if (
            due_date < academic_term.start_date
            or due_date > academic_term.end_date
        ):

            raise forms.ValidationError(
                "Due date must be inside the selected academic term."
            )

        return cleaned_data

    def save(self, commit=True):

        fee_structure = super().save(
            commit=False
        )

        if (
            self.current_user
            and not self.current_user.groups.filter(
                name="Product Owner"
            ).exists()
        ):

            fee_structure.tenant = (
                self.current_user.tenant
            )

        if commit:

            fee_structure.save()

        return fee_structure


class StudentFeeForm(forms.ModelForm):

    class Meta:

        model = StudentFee

        fields = [
            "tenant",
            "student",
            "fee_structure",
        ]

    def __init__(
        self,
        *args,
        current_user=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:

            self.fields["tenant"].queryset = Tenant.objects.all()

            self.fields["student"].queryset = (
                Student.objects.filter(
                    is_active=True
                )
            )

            self.fields["fee_structure"].queryset = (
                FeeStructure.objects.filter(
                    is_active=True
                )
            )

        else:

            tenant = current_user.tenant

            self.fields["tenant"].initial = tenant
            self.fields["tenant"].disabled = True

            self.fields["student"].queryset = (
                Student.objects.filter(
                    tenant=tenant,
                    is_active=True,
                )
            )

            self.fields["fee_structure"].queryset = (
                FeeStructure.objects.filter(
                    tenant=tenant,
                    is_active=True,
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        tenant = cleaned_data.get(
            "tenant"
        )

        student = cleaned_data.get(
            "student"
        )

        fee_structure = cleaned_data.get(
            "fee_structure"
        )

        if not all([
            tenant,
            student,
            fee_structure,
        ]):
            return cleaned_data

        if student.tenant != tenant:

            raise forms.ValidationError(
                "Student must belong to the selected tenant."
            )

        if fee_structure.tenant != tenant:

            raise forms.ValidationError(
                "Fee structure must belong to the selected tenant."
            )

        if student.school_class != fee_structure.school_class:

            raise forms.ValidationError(
                "Selected fee structure does not belong to the student's class."
            )

        duplicate_fee = StudentFee.objects.filter(
            student=student,
            fee_structure=fee_structure,
        )

        if self.instance.pk:

            duplicate_fee = duplicate_fee.exclude(
                pk=self.instance.pk
            )

        if duplicate_fee.exists():

            raise forms.ValidationError(
                "This fee has already been assigned to this student."
            )

        return cleaned_data

    def save(self, commit=True):

        student_fee = super().save(
            commit=False
        )

        student_fee.tenant = (
            student_fee.student.tenant
        )

        student_fee.total_amount = (
            student_fee.fee_structure.amount
        )

        if commit:

            student_fee.save()

        return student_fee


class FeePaymentForm(forms.ModelForm):

    class Meta:

        model = FeePayment

        fields = [
            "student_fee",
            "amount_paid",
            "payment_date",
            "payment_method",
            "reference_number",
            "remarks",
        ]

        widgets = {
            "payment_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(
        self,
        *args,
        current_user=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:

            self.fields["student_fee"].queryset = (
                StudentFee.objects.all()
            )

        else:

            self.fields["student_fee"].queryset = (
                StudentFee.objects.filter(
                    tenant=current_user.tenant
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        student_fee = cleaned_data.get(
            "student_fee"
        )

        amount_paid = cleaned_data.get(
            "amount_paid"
        )

        if not all([
            student_fee,
            amount_paid,
        ]):
            return cleaned_data

        if amount_paid <= 0:

            raise forms.ValidationError(
                "Payment amount must be greater than zero."
            )

        if amount_paid > student_fee.balance_amount:

            raise forms.ValidationError(
                "Payment amount cannot be greater than the remaining balance."
            )

        return cleaned_data

    def save(self, commit=True):

        payment = super().save(
            commit=False
        )

        if self.current_user:

            payment.recorded_by = (
                self.current_user
            )

        if commit:

            payment.save()

        return payment
class BulkStudentFeeAssignForm(forms.Form):

    fee_structure = forms.ModelChoiceField(
        queryset=FeeStructure.objects.none(),
        label="Fee Structure",
    )

    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        required=False,
        label="Section",
        help_text="Leave empty to assign fee to all students in the selected class.",
    )

    def __init__(self, *args, current_user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:

            self.fields["fee_structure"].queryset = (
                FeeStructure.objects.filter(
                    is_active=True
                ).select_related(
                    "tenant",
                    "academic_term",
                    "school_class",
                )
            )

            self.fields["section"].queryset = (
                Section.objects.all()
            )

        else:

            tenant = current_user.tenant

            self.fields["fee_structure"].queryset = (
                FeeStructure.objects.filter(
                    tenant=tenant,
                    is_active=True,
                ).select_related(
                    "tenant",
                    "academic_term",
                    "school_class",
                )
            )

            self.fields["section"].queryset = (
                Section.objects.filter(
                    school_class__tenant=tenant,
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        fee_structure = cleaned_data.get("fee_structure")
        section = cleaned_data.get("section")

        if not fee_structure:
            return cleaned_data

        if section and section.school_class != fee_structure.school_class:

            raise forms.ValidationError(
                "Selected section does not belong to the selected fee structure class."
            )

        return cleaned_data
class BookCategoryForm(forms.ModelForm):

    class Meta:
        model = BookCategory

        fields = [
            "tenant",
            "category_name",
            "description",
            "is_active",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, current_user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:

            self.fields["tenant"].queryset = Tenant.objects.all()

        else:

            self.fields["tenant"].initial = current_user.tenant
            self.fields["tenant"].disabled = True

    def save(self, commit=True):

        category = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(name="Product Owner").exists()
        ):
            category.tenant = self.current_user.tenant

        if commit:
            category.save()

        return category


class BookForm(forms.ModelForm):

    class Meta:
        model = Book

        fields = [
            "tenant",
            "category",
            "title",
            "author",
            "isbn",
            "publisher",
            "publication_year",
            "total_copies",
            "shelf_location",
            "is_active",
        ]

    def __init__(self, *args, current_user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:

            self.fields["tenant"].queryset = Tenant.objects.all()
            self.fields["category"].queryset = BookCategory.objects.filter(
                is_active=True
            )

        else:

            tenant = current_user.tenant

            self.fields["tenant"].initial = tenant
            self.fields["tenant"].disabled = True

            self.fields["category"].queryset = BookCategory.objects.filter(
                tenant=tenant,
                is_active=True,
            )

    def clean(self):

        cleaned_data = super().clean()

        tenant = cleaned_data.get("tenant")
        category = cleaned_data.get("category")
        total_copies = cleaned_data.get("total_copies")

        if total_copies is not None and total_copies <= 0:
            raise forms.ValidationError(
                "Total copies must be greater than zero."
            )

        if tenant and category and category.tenant != tenant:
            raise forms.ValidationError(
                "Book category must belong to the selected tenant."
            )

        if self.instance.pk and total_copies is not None:

            old_book = Book.objects.get(pk=self.instance.pk)

            borrowed_copies = old_book.total_copies - old_book.available_copies

            if total_copies < borrowed_copies:
                raise forms.ValidationError(
                    "Total copies cannot be less than currently borrowed copies."
                )

        return cleaned_data

    def save(self, commit=True):

        book = super().save(commit=False)

        if (
            self.current_user
            and not self.current_user.groups.filter(name="Product Owner").exists()
        ):
            book.tenant = self.current_user.tenant

        if book.pk:

            old_book = Book.objects.get(pk=book.pk)
            borrowed_copies = old_book.total_copies - old_book.available_copies
            book.available_copies = book.total_copies - borrowed_copies

        else:

            book.available_copies = book.total_copies

        if commit:
            book.save()

        return book


class LibraryIssueForm(forms.ModelForm):

    class Meta:
        model = LibraryIssue

        fields = [
            "book",
            "member_type",
            "student",
            "teacher",
            "issue_date",
            "due_date",
            "remarks",
        ]

        widgets = {
            "issue_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, current_user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        if current_user is None:
            return

        is_product_owner = current_user.groups.filter(
            name="Product Owner"
        ).exists()

        if is_product_owner:

            self.fields["book"].queryset = Book.objects.filter(
                is_active=True,
                available_copies__gt=0,
            )

            self.fields["student"].queryset = Student.objects.filter(
                is_active=True,
            )

            self.fields["teacher"].queryset = Teacher.objects.filter(
                is_active=True,
            )

        else:

            tenant = current_user.tenant

            self.fields["book"].queryset = Book.objects.filter(
                tenant=tenant,
                is_active=True,
                available_copies__gt=0,
            )

            self.fields["student"].queryset = Student.objects.filter(
                tenant=tenant,
                is_active=True,
            )

            self.fields["teacher"].queryset = Teacher.objects.filter(
                tenant=tenant,
                is_active=True,
            )

    def clean(self):

        cleaned_data = super().clean()

        book = cleaned_data.get("book")
        member_type = cleaned_data.get("member_type")
        student = cleaned_data.get("student")
        teacher = cleaned_data.get("teacher")
        issue_date = cleaned_data.get("issue_date")
        due_date = cleaned_data.get("due_date")

        if book and book.available_copies <= 0:
            raise forms.ValidationError(
                "This book is not available right now."
            )

        if issue_date and due_date and due_date < issue_date:
            raise forms.ValidationError(
                "Due date cannot be before issue date."
            )

        if member_type == "Student":

            if not student:
                raise forms.ValidationError(
                    "Please select a student."
                )

            if teacher:
                raise forms.ValidationError(
                    "Teacher field must be empty when member type is Student."
                )

            if book and student.tenant != book.tenant:
                raise forms.ValidationError(
                    "Student must belong to the same tenant as the book."
                )

        if member_type == "Teacher":

            if not teacher:
                raise forms.ValidationError(
                    "Please select a teacher."
                )

            if student:
                raise forms.ValidationError(
                    "Student field must be empty when member type is Teacher."
                )

            if book and teacher.tenant != book.tenant:
                raise forms.ValidationError(
                    "Teacher must belong to the same tenant as the book."
                )

        return cleaned_data


class ReturnBookForm(forms.ModelForm):

    class Meta:
        model = LibraryIssue

        fields = [
            "return_date",
            "fine_amount",
            "remarks",
        ]

        widgets = {
            "return_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        return_date = cleaned_data.get("return_date")
        fine_amount = cleaned_data.get("fine_amount")

        if return_date and return_date < self.instance.issue_date:
            raise forms.ValidationError(
                "Return date cannot be before issue date."
            )

        if fine_amount is not None and fine_amount < 0:
            raise forms.ValidationError(
                "Fine amount cannot be negative."
            )

        return cleaned_data
class AnnouncementForm(forms.ModelForm):

    class Meta:
        model = Announcement

        fields = [
            "tenant",
            "title",
            "message",
            "target_role",
            "priority",
            "start_date",
            "end_date",
            "is_active",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                }
            ),
        }

    def __init__(self, *args, current_user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        for field_name, field in self.fields.items():

            field.widget.attrs.update(
                {
                    "class": "form-control",
                }
            )

        if current_user is None:
            return

        if current_user.groups.filter(name="School Admin").exists():

            self.fields["tenant"].initial = current_user.tenant
            self.fields["tenant"].disabled = True

    def clean(self):

        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:

            raise forms.ValidationError(
                "End date cannot be before start date."
            )

        return cleaned_data

    def save(self, commit=True):

        announcement = super().save(
            commit=False
        )

        if (
            self.current_user
            and self.current_user.groups.filter(name="School Admin").exists()
        ):

            announcement.tenant = self.current_user.tenant

        if self.current_user:

            if announcement.created_by is None:

                announcement.created_by = self.current_user

        if commit:

            announcement.save()

        return announcement