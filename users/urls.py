from django.urls import path
from .views import register_view, loigin_view

urlpatterns = [
    path("registration/", register_view, name="register_view"),
    path("login/", loigin_view, name="login_view"),
]
