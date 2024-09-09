from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password

from django_countries.fields import CountryField
from shop.models import Product


class CustomUserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if kwargs.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **kwargs)


class User(AbstractUser):
    email = models.EmailField("Email", unique=True, null=False, blank=False)
    full_name = models.CharField("Full name", max_length=100, null=True, blank=True)
    mobile_phone = models.IntegerField("Phone number", null=True, blank=True)
    avatar = models.ImageField("Avatar", upload_to='users/avatar', default='users/default/user-avatar.png', blank=True)
    place_of_delivery = models.CharField("Place of Delivery", max_length=100, null=True, blank=True)
    postal_code = models.PositiveIntegerField("Postal Code", null=True, blank=True)
    country = CountryField("Country", null=True, blank=True)
    username = models.CharField("Username", max_length=100, unique=True, null=True, blank=True)

    first_name = None
    last_name = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email