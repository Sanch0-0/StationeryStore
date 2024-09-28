from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from .models import User



class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This username is already taken.")]
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="This email is already registered.")
        ]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    mobile_phone = serializers.CharField(required=False)
    full_name = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    postal_code = serializers.CharField(required=True)
    place_of_delivery = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'mobile_phone', 'full_name', 'country', 'postal_code', 'place_of_delivery'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            full_name=validated_data.get('full_name'),
            mobile_phone=validated_data.get('mobile_phone', None),
            country=validated_data.get('country'),
            postal_code=validated_data.get('postal_code'),
            place_of_delivery=validated_data.get('place_of_delivery'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ['username', 'password']

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'full_name', 'mobile_phone', 'country', 'place_of_delivery', 'postal_code', 'avatar']

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
