from django.urls import path

from .views import students, teachers

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
]