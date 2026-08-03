from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render

from core.models import Student, Teacher


class UserLoginView(LoginView):
    template_name = "accounts/login.html"


@login_required
def dashboard(request):

    student_count = Student.objects.count()
    teacher_count = Teacher.objects.count()

    user_group = "No Role"

    if request.user.groups.exists():
        user_group = request.user.groups.first().name

    context = {
        "student_count": student_count,
        "teacher_count": teacher_count,
        "user_group": user_group,
    }

    return render(
        request,
        "accounts/dashboard.html",
        context,
    )