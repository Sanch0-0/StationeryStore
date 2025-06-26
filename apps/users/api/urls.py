from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .views import *

router = DefaultRouter()
router.register(r'login', LoginViewSet, basename='login')
router.register(r'logout', LogoutViewSet, basename='logout')
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'profile', UpdateProfileViewSet, basename='update')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]