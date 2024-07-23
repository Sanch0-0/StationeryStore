from django.urls import path
from .views import (
    register_view,
    loigin_view,
    logout_view,
    logout_apply_view,
)
urlpatterns = [
    path("registration/", register_view, name="registration"),
    path("login/", loigin_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("logout/apply/", logout_apply_view, name="logout_apply"),
]
