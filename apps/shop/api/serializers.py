from shop.models import Category, Product, ReviewRating
from shop.filters import ProductsFilter
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'image', 'name',
                  'description', 'price', 'discount',
                  'category', 'brand','price_with_discount', 'average_rating')


class ReviewRatingSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ReviewRating
        fields = ['id', 'product', 'user', 'review', 'rating', 'created_at']

    def validate_rating(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("Raiting must be integer!")
        if value < 1 or value > 5:
            raise serializers.ValidationError("Min raiting value is 1, max is 5!")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductFilterSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    price__gt = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    price__lt = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    has_discount = serializers.BooleanField(required=False)
    category = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    brand = serializers.CharField(required=False)

    # Sorting options
    ordering = serializers.ChoiceField(
        choices=['price', '-price', 'created_at', '-created_at', 'name', '-name', 'random'],
        required=False
    )

    def filter_queryset(self, queryset):
        # Apply filters using the ProductFilter from filters.py
        filter_data = {
            key: value for key, value in self.validated_data.items()
            if key in ['name', 'price__gt', 'price__lt', 'has_discount', 'category', 'brand']
        }
        filter_set = ProductsFilter(filter_data, queryset=queryset)
        filtered_queryset = filter_set.qs

        # Apply sorting
        ordering = self.validated_data.get('ordering')
        if ordering == 'random':
            filtered_queryset = filtered_queryset.order_by('?')
        elif ordering:
            filtered_queryset = filtered_queryset.order_by(ordering)

        return filtered_queryset