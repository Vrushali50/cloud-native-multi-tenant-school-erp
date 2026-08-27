from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import UserLoginView, dashboard, user_list, add_user, edit_user, toggle_user_status, teacher_dashboard, student_dashboard


app_name = "accounts"


urlpatterns = [
    path(
        "login/",
        UserLoginView.as_view(),
        name="login",
    ),
    path(
        "dashboard/",
        dashboard,
        name="dashboard",
    ),
    path(
        "users/",
        user_list,
        name="user_list",
    ),
    path(
        "users/add/",
        add_user,
        name="add_user",
    
    ),

    path(
    "users/<int:user_id>/edit/",
    edit_user,
    name="edit_user",
    ),

    path(
        "logout/",
        LogoutView.as_view(next_page="accounts:login"),
        name="logout",
    ),

    path(
    "users/<int:user_id>/status/",
    toggle_user_status,
    name="toggle_user_status",
    ),
    path(
        "teacher-dashboard/",
        teacher_dashboard,
        name="teacher_dashboard",
    ),

    path(
        "student-dashboard/",
        student_dashboard,
        name="student_dashboard",
    ),
]