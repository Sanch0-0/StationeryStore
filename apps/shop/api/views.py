from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.mixins import ListModelMixin
from core.permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework import status, viewsets
from core.tasks import log_task
from apps.shop.models import *
from .serializers import *


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]


class ReviewRatingViewSet(viewsets.ModelViewSet):
    queryset = ReviewRating.objects.all()
    serializer_class = ReviewRatingSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductFilterViewSet(ListModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        # Use ProductFilterSerializer for filtering input validation,
        # and ProductSerializer for the actual product data response.
        if self.action == 'list':
            return ProductSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        # Use ProductFilterSerializer to handle filtering and sorting
        filter_serializer = ProductFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        log_task(f"User {request.user.username if request.user.is_authenticated else 'Anonymous'} is filtering products with parameters {request.query_params}.", "debug")

        # Get the filtered and sorted queryset
        queryset = filter_serializer.filter_queryset(self.queryset)

        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serialize the data without pagination
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)