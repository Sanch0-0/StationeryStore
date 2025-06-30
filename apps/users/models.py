from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django_countries.fields import CountryField
from django.core.validators import RegexValidator


class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **kwargs):
        if not email:
            raise ValueError("The Email field must be set!")
        if not username:
            raise ValueError("The Username field must be set!")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if kwargs.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **kwargs)


class User(AbstractUser):
    username = models.CharField("Username", max_length=30,unique=True, blank=True, null=True)
    email = models.EmailField("Email", unique=True, null=False, blank=False)
    full_name = models.CharField("Full name", max_length=100, null=True, blank=True)
    mobile_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\d{10,15}$',
        message="Phone number must be up to 15 digits.")],
        blank=True
    )
    avatar = models.ImageField("Avatar", upload_to='users/avatar', default='users/default/user-avatar.png', blank=True)
    place_of_delivery = models.CharField("Place of Delivery", max_length=100, null=True, blank=True)
    postal_code = models.PositiveIntegerField("Postal Code", null=True, blank=True)
    country = CountryField("Country", null=True, blank=True)

    first_name = None
    last_name = None

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.username if self.username else str(self.pk)
