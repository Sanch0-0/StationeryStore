from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *


router = DefaultRouter()
router.register(r'review', ReviewRatingViewSet, basename='review')
router.register(r'filters', ProductFilterViewSet, basename='filters')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'product', ProductViewSet, basename='producrt')

urlpatterns = [
    path('', include(router.urls)),
]