from django.db.models import F
from shop.filters import ProductsFilter
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import RegexValidator
from rest_framework import serializers
from shop.models import Category, Product, ReviewRating
from favourite.models import Favourite, FavouriteProduct
from cart.models import Cart, CartItem

User = get_user_model()

#! Users serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'mobile_phone', 'country', 'place_of_delivery', 'postal_code', 'avatar', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    mobile_phone = serializers.CharField(
        label="Mobile phone",
        validators=[RegexValidator(regex=r'^\d{10,15}$', message="Phone number must start from 0, up to 15 digits allowed.")]
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password1', 'password2',
            'mobile_phone', 'full_name', 'country', 'postal_code', 'place_of_delivery'
        ]
    def validate_mobile_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("The phone number should contain only digits.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        # Удаляем password1 и password2, так как они не нужны для создания пользователя
        password = validated_data.pop('password1')
        validated_data.pop('password2')  # Удаляем password2, так как он не нужен

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username_or_email'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError("Invalid credentials. Please try again.")
        attrs['user'] = user
        return attrs


class UpdateProfileSerializer(serializers.ModelSerializer):
    country = serializers.CharField(allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'mobile_phone', 'country', 'place_of_delivery', 'postal_code', 'avatar']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert country object to its string representation (like 'US' or 'United States')
        representation['country'] = instance.country.name if instance.country else None
        return representation

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.mobile_phone = validated_data.get('mobile_phone', instance.mobile_phone)
        instance.country = validated_data.get('country', instance.country)
        instance.place_of_delivery = validated_data.get('place_of_delivery', instance.place_of_delivery)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance



#! Shop serializers
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



#! Favourites serializers
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


#! Cart serializers

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
