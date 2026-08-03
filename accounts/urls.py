from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import UserLoginView, dashboard


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
        "logout/",
        LogoutView.as_view(next_page="accounts:login"),
        name="logout",
    ),
]