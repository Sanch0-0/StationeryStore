from rest_framework import serializers
from apps.cart.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=False)
    name = serializers.CharField(source='product.name', read_only=True)
    price_with_discount = serializers.FloatField(source='product.price_with_discount', read_only=True)
    category = serializers.CharField(source='product.category.name', read_only=True)
    brand = serializers.CharField(source='product.brand.name', read_only=True)
    average_rating = serializers.FloatField(source='product.average_rating', read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product_id', 'name', 'price_with_discount', 'quantity', 'category', 'brand', 'average_rating')


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'cart_items', 'total_quantity', 'total_price')

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.cart_items.all())

    def get_total_price(self, obj):
        return sum(item.product.price_with_discount * item.quantity for item in obj.cart_items.all())

    def create(self, validated_data):
        user = self.context['request'].user
        cart, created = Cart.objects.get_or_create(user=user)
        return cart