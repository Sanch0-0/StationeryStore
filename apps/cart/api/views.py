from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from core.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from core.tasks import log_task
from apps.cart.models import *
from .serializers import *


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