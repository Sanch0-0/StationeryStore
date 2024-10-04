from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from django.conf import settings
from .permissions import IsSuperUser
from django.contrib.auth.backends import ModelBackend
from shop.models import Category, Product, ReviewRating
from .serializers import ProductSerializer, CategorySerializer
from django.contrib.auth import get_user_model, authenticate, login
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProductSerializer,
    CategorySerializer,
    UpdateProfileSerializer)


User = get_user_model()

#! User views set
class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Registration successful!",
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
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': "Succesfully logged in!",
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

            # Создаем токен для пользователя
            token = RefreshToken(refresh_token)

            # Добавляем токен в черный список
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

        except (TokenError, InvalidToken):
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['put', 'get'], url_path='profile/update')
    def update_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UpdateProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    "user": serializer.data,
                    "message": "Profile updated successfully!"
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#! Shop views set
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUser]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUser]


#! Favourite views set


#! Cart views set
