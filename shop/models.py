from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg, Count
from image_cropping import ImageRatioField


class Category(models.Model):
    name = models.CharField(verbose_name="name", max_length=30)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    image = models.ImageField(verbose_name="image", upload_to="products")
    cropping = ImageRatioField('image', '200x200', verbose_name="cropping")
    name = models.CharField(verbose_name="name", max_length=50)
    description = models.TextField(verbose_name="description")
    price = models.DecimalField(verbose_name="price", max_digits=7, decimal_places=2, default=1, blank=True)
    discount = models.SmallIntegerField(verbose_name="discount", default=0, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    created_at = models.DateTimeField(verbose_name="Created at", default=timezone.now, blank=True)

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    @property
    def price_with_discount(self):
        return self.price - (self.price * self.discount / 100)

    @property
    def average_rating(self):
        total_ratings = self.ratings.count()
        if total_ratings > 0:
            total_score = sum(rating.value for rating in self.ratings.all())
            return round(total_score / total_ratings, 1)
        return 0.0

    @classmethod
    def top_rated_products(cls, limit=4):
        # Annotate products with their average rating and the number of ratings
        return cls.objects.annotate(
            avg_rating=Avg('ratings__value'),
            rating_count=Count('ratings')
        ).filter(
            avg_rating__gt=4.5,  # Only include products with an average rating greater than 4.5
            rating_count__gt=0    # Exclude products with no ratings
        ).order_by('-avg_rating')[:limit]


class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(default=0)  # rating value from 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # ensures a user can only rate a product once

    def __str__(self):
        return f"{self.user.username} rated {self.product.name} {self.value} stars"
