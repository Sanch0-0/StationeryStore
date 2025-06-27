from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from core.tasks import log_task
from apps.cart.models import *
from .serializers import *


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