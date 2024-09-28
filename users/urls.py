from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    register_view,
    login_view,
    logout_view,
    logout_apply_view,
    profile_view,
    update_profile,
    UserViewSet
)

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path("registration/", register_view, name="registration"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("logout/apply/", logout_apply_view, name="logout_apply"),
    path("profile/", profile_view, name="profile"),
    path("profile/update",  update_profile, name="update_profile"),
    path('api/', include(router.urls)),
]
