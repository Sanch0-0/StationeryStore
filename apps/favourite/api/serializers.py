from apps.favourite.models import Favourite, FavouriteProduct
from rest_framework import serializers


class FavouriteProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=False)
    name = serializers.CharField(source='product.name', read_only=True)
    price_with_discount = serializers.FloatField(source='product.price_with_discount', read_only=True)
    category = serializers.CharField(source='product.category.name', read_only=True)
    brand = serializers.CharField(source='product.brand.name', read_only=True)
    average_rating = serializers.FloatField(source='product.average_rating', read_only=True)

    class Meta:
        model = FavouriteProduct
        fields = ('id', 'product_id', 'name', 'price_with_discount', 'quantity', 'category', 'brand', 'average_rating')

class FavouriteSerializer(serializers.ModelSerializer):
    favourite_items = FavouriteProductSerializer(many=True, read_only=True)
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Favourite
        fields = ('id', 'favourite_items', 'total_quantity', 'total_price')

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.favourite_items.all())

    def get_total_price(self, obj):
        return sum(item.product.price_with_discount * item.quantity for item in obj.favourite_items.all())

    def create(self, validated_data):
        user = self.context['request'].user
        favourite, created = Favourite.objects.get_or_create(user=user)
        return favourite