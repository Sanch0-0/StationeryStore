from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
