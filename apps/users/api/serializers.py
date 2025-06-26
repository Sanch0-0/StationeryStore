from django.contrib.auth import get_user_model, authenticate
from django.core.validators import RegexValidator
from rest_framework import serializers


User = get_user_model()


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
        # Deleting password1 and password2
        password = validated_data.pop('password1')
        validated_data.pop('password2')  # Deleting password2

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
    avatar = serializers.ImageField(required=False)

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

        # Update the avatar only if a new file is provided
        avatar = validated_data.get('avatar')
        if avatar:
            instance.avatar = avatar

        instance.save()
        return instance