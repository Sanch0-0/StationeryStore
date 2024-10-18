from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout

from .serializers import *
from .permissions import IsOwnerOrReadOnly
from shop.models import Category, Product, ReviewRating
# from favourite.models import Favourite, FavouriteProduct
from .serializers import ProductSerializer, CategorySerializer


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
            user = serializer.validated_data['user']

            # Проверка наличия активного refresh токена
            if OutstandingToken.objects.filter(user_id=user.id).exists() and not BlacklistedToken.objects.filter(token__user_id=user.id).exists():
                return Response({
                    'message': "User is already logged in.",
                    'access': str(RefreshToken.for_user(user).access_token),
                }, status=status.HTTP_200_OK)

            # Если нет активного токена, создаем новые токены
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': "Successfully logged in!",
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

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




#! Cart views set
class CartViewSet(viewsets.ViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        # Получаем корзину текущего пользователя
        user = request.user
        cart = get_object_or_404(Cart, user=user)

        # Ищем элемент корзины по id (pk)
        cart_item = get_object_or_404(CartItem, cart=cart, id=pk)

        # Сериализуем найденный элемент
        serializer = CartItemSerializer(cart_item)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity')

            # Получаем или создаем корзину текущего пользователя
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Обновляем или создаем элемент в корзине
            cart_item, item_created = CartItem.objects.update_or_create(
                cart=cart, product_id=product_id,
                defaults={'quantity': quantity}
            )

            # Сериализуем созданный или обновленный элемент корзины
            item_serializer = CartItemSerializer(cart_item, context={'request': request})

            return Response({
                'detail': "Product added to cart successfully.",
                'cart_item': item_serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user
        cart = get_object_or_404(Cart, user=user)

        # Получаем элемент корзины
        cart_item = get_object_or_404(CartItem, cart=cart, id=pk)
        cart_item.quantity = request.data.get('quantity', cart_item.quantity)
        cart_item.save()

        item_serializer = CartItemSerializer(cart_item, context={'request': request})

        return Response({
            'detail': 'Quantity updated successfully.',
            'cart_item': item_serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItem, cart=cart, id=pk)
        cart_item.delete()
        return Response({'detail': 'Item removed from cart.'}, status=status.HTTP_204_NO_CONTENT)




#! Favourite views set
class FavouriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteProductSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        user = request.user
        favourite = get_object_or_404(Favourite, user=user)

        favourite_product = get_object_or_404(FavouriteProduct, favourite=favourite, id=pk)

        serializer = FavouriteProductSerializer(favourite_product)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        user = request.user
        favourite, created = Favourite.objects.get_or_create(user=user)
        serializer = FavouriteSerializer(favourite)
        return Response(serializer.data)

    def get_queryset(self):
        return FavouriteProduct.objects.filter(cart__user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = FavouriteProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity')

            favourite, created = Favourite.objects.get_or_create(user=request.user)

            favourite_product, product_created = FavouriteProduct.objects.update_or_create(
                favourite=favourite, product_id=product_id,
                defaults={'quantity': quantity}
            )

            product_serializer = FavouriteProductSerializer(favourite_product, context={'request': request})

            return Response({
                'detail': "Product added to favourite successfully.",
                'favourite_product': product_serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user
        favourite = get_object_or_404(Favourite, user=user)

        favourite_product = get_object_or_404(FavouriteProduct, favourite=favourite, id=pk)

        favourite_product.quantity = request.data.get('quantity', favourite_product.quantity)
        favourite_product.save()

        product_serializer = FavouriteProductSerializer(favourite_product, context={'request': request})

        return Response({
            'detail': 'Quantity updated successfully.',
            'favourite_product': product_serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        user = request.user
        favourite = get_object_or_404(Favourite, user=user)
        favourite_product = get_object_or_404(FavouriteProduct, favourite=favourite, id=pk)
        favourite_product.delete()
        return Response({'detail': 'Item removed from favourites.'}, status=status.HTTP_204_NO_CONTENT)
