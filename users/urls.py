from django.urls import path
from .views import (
    register_view,
    loigin_view,
    logout_view,
    logout_apply_view,
    update_view,
    profile_view,
)
urlpatterns = [
    path("registration/", register_view, name="registration"),
    path("login/", loigin_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("logout/apply/", logout_apply_view, name="logout_apply"),
    path("update", update_view, name="update_profile"),
    path("profile/", profile_view, name="profile"),
]
