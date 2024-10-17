from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser

from .serializers import *
from django.conf import settings
from shop.models import Category, Product, ReviewRating
from .serializers import ProductSerializer, CategorySerializer
from django.contrib.auth import get_user_model, authenticate, login, logout
from .permissions import IsOwnerOrReadOnly


User = get_user_model()

#! User views set
class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        refresh = RefreshToken.for_user(user)

        user_serializer = UserSerializer(user)
        return Response({
            "message": "Registration successful!",
            "user": user_serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username_or_email'], password=serializer.validated_data['password'])

            if user is not None:
                # Проверка наличия активного refresh токена
                if OutstandingToken.objects.filter(user=user).exists() and not BlacklistedToken.objects.filter(user=user).exists():
                    return Response({
                        'message': "User is already logged in.",
                        'access': str(RefreshToken.for_user(user).access_token),
                    }, status=status.HTTP_200_OK)

                # Если нет активного токена, создаем новые токены
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': "Successfully logged in!",
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)

            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            # Получаем refresh-токен из тела запроса
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

        except (TokenError, InvalidToken):
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileViewSet(RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        return self.request.user




#! Shop views set
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


    
#! Favourite views set


#! Cart views set
