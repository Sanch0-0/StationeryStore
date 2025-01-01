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
from .serializers import ProductSerializer, CategorySerializer
from main.tasks import log_task


User = get_user_model()

#! User views set
class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            log_task(f"Authenticated user {request.user.username} attempted to register. Logging out...", 'warning')
            logout(request)
            log_task(f"User {request.user.username} has been logged out", 'info')

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            log_task(f"User {user.username} registered successfully.", 'info')
        except Exception as e:
            log_task(f"Error during registration: {str(e)}", 'error')
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # New user authorizating
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # JWT token generation
        refresh = RefreshToken.for_user(user)
        log_task(f"Tokens generated for user {user.username}: Refresh: {refresh}, Access: {refresh.access_token}", 'debug')

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

            # Check for active refresh token
            if OutstandingToken.objects.filter(user_id=user.id).exists() and not BlacklistedToken.objects.filter(token__user_id=user.id).exists():
                log_task(f"Authenticated user {user.username} attempted to log in.", 'warning')
                return Response({
                    'message': "User is already logged in.",
                    'access': str(RefreshToken.for_user(user).access_token),
                }, status=status.HTTP_200_OK)

            # Create new tokens if no active
            refresh = RefreshToken.for_user(user)
            log_task(f"Tokens generated for user {user.username}: Refresh: {refresh}, Access: {refresh.access_token}", 'debug')
            log_task(f"User {user.username} successfully logged in.", 'info')

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
            # Get the refresh token from the request body
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                log_task(f"User {request.user.username} did not provide a refresh token.", 'warning')
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            log_task(f"Refresh token for user {request.user.username} successfully blacklisted.", 'info')

            # Inform the client to clear the access token
            log_task(f"User {request.user.username} has been successfully loged out.", 'info')
            return Response({"detail": "Successfully logged out from account."}, status=status.HTTP_205_RESET_CONTENT)

        except (TokenError, InvalidToken):
            log_task(f"Logout failed for user {request.user.username} due to an invalid token: {str(e)}.", 'error')
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileViewSet(RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        log_task(f"User {self.request.user.username} changed the profile.", 'info')
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




#! Cart views set
class CartViewSet(viewsets.ViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        user = request.user
        cart = get_object_or_404(Cart, user=user)

        # Retrieve the cart item by its id (pk)
        cart_item = get_object_or_404(CartItem, cart=cart, id=pk)

        serializer = CartItemSerializer(cart_item)

        log_task(f"User {user.username} retrieved cart item with ID {pk}.", "info")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        # Get or create the current user's cart
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)

        serializer = CartSerializer(cart)

        log_task(f"User {user.username} retrieved his/her cart.", "info")
        return Response(serializer.data)

    def get_queryset(self):
        # Return all cart items for the current user's cart
        return CartItem.objects.filter(cart__user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity')

            # Get or create the current user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Update or create a cart item in the cart
            cart_item, item_created = CartItem.objects.update_or_create(
                cart=cart, product_id=product_id,
                defaults={'quantity': quantity}
            )

            # Serialize the created or updated cart item
            item_serializer = CartItemSerializer(cart_item, context={'request': request})

            action = "created" if item_created else "updated"
            log_task(f"User {request.user.username} {action} cart item for product ID {product_id} with quantity {quantity}.", "info")

            return Response({
                'detail': "Product added to cart successfully.",
                'cart_item': item_serializer.data
            }, status=status.HTTP_201_CREATED)

        log_task(f"Failed to add product to cart for user {request.user.username}. Errors: {serializer.errors}", "error")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user
        cart = get_object_or_404(Cart, user=user)

        # Retrieve the cart item
        cart_item = get_object_or_404(CartItem, cart=cart, id=pk)
        cart_item.quantity = request.data.get('quantity', cart_item.quantity)
        cart_item.save()

        item_serializer = CartItemSerializer(cart_item, context={'request': request})

        log_task(f"User {user.username} updated quantity of cart item with ID {pk} to {cart_item.quantity}.", "info")
        return Response({
            'detail': 'Quantity updated successfully.',
            'cart_item': item_serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        user = request.user
        cart = get_object_or_404(Cart, user=user)

        # Retrieve the cart item to be deleted
        cart_item = get_object_or_404(CartItem, cart=cart, id=pk)
        cart_item.delete()

        log_task(f"User {user.username} removed cart item with ID {pk}.", "info")
        return Response({'detail': 'Item removed from cart.'}, status=status.HTTP_204_NO_CONTENT)




#! Favourite views set
class FavouriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteProductSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        user = request.user
        favourite = get_object_or_404(Favourite, user=user)

        # Retrieve a specific favourite product by ID
        favourite_product = get_object_or_404(FavouriteProduct, favourite=favourite, id=pk)
        serializer = FavouriteProductSerializer(favourite_product)

        log_task(f"User {user.username} retrieved favourite product with ID {pk}.", "info")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        user = request.user

        # Retrieve or create the user's favourites
        favourite, created = Favourite.objects.get_or_create(user=user)
        serializer = FavouriteSerializer(favourite)

        log_task(f"User {user.username} retrieved his/her favourite list.", "info")
        return Response(serializer.data)

    def get_queryset(self):
        # Filter the favourite products based on the current user
        return FavouriteProduct.objects.filter(favourite__user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = FavouriteProductSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Get the product ID and quantity from the request
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity')

            # Retrieve or create the user's favourites
            favourite, created = Favourite.objects.get_or_create(user=request.user)

            # Update or create the favourite product
            favourite_product, product_created = FavouriteProduct.objects.update_or_create(
                favourite=favourite, product_id=product_id,
                defaults={'quantity': quantity}
            )

            # Serialize the created or updated favourite product
            product_serializer = FavouriteProductSerializer(favourite_product, context={'request': request})

            action = "added" if product_created else "updated"
            log_task(
                f"User {request.user.username} {action} product with ID {product_id} to favourites. Quantity: {quantity}.",
                "info"
            )
            return Response({
                'detail': "Product added to favourites successfully.",
                'favourite_product': product_serializer.data
            }, status=status.HTTP_201_CREATED)

        log_task(f"User {request.user.username} encountered errors while adding a product to favourites: {serializer.errors}.", "error")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user
        favourite = get_object_or_404(Favourite, user=user)

        # Retrieve the specific favourite product to update
        favourite_product = get_object_or_404(FavouriteProduct, favourite=favourite, id=pk)

        # Update the product quantity
        favourite_product.quantity = request.data.get('quantity', favourite_product.quantity)
        favourite_product.save()

        # Serialize the updated product
        product_serializer = FavouriteProductSerializer(favourite_product, context={'request': request})

        log_task(f"User {user.username} updated quantity for favourite product with ID {pk}.", "info")
        return Response({
            'detail': 'Quantity updated successfully.',
            'favourite_product': product_serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        user = request.user
        favourite = get_object_or_404(Favourite, user=user)

        # Retrieve the specific favourite product to delete
        favourite_product = get_object_or_404(FavouriteProduct, favourite=favourite, id=pk)
        favourite_product.delete()

        log_task(f"User {user.username} removed favourite product with ID {pk}.", "info")
        return Response({'detail': 'Item removed from favourites.'}, status=status.HTTP_204_NO_CONTENT)
