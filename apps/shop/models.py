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
    name = models.CharField(verbose_name="name", max_length=30)
    description = models.TextField(verbose_name="description")
    price = models.DecimalField(verbose_name="price", max_digits=7, decimal_places=2, default=1, blank=True, db_index=True)
    discount = models.SmallIntegerField(verbose_name="discount", default=0, blank=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", db_index=True)
    brand = models.CharField(verbose_name='brand', max_length=20, db_index=True)
    created_at = models.DateTimeField(verbose_name="Created at", default=timezone.now, blank=True, db_index=True)

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    @property
    def price_with_discount(self):
        return self.price - (self.price * self.discount / 100)

    @property
    def average_rating(self):
        total_ratings = self.review_ratings.count()
        if total_ratings > 0:
            total_score = sum(rating.rating for rating in self.review_ratings.all())
            return round(total_score / total_ratings, 1)
        return 0.0

    @classmethod
    def top_rated_products(cls, limit=4):
        return cls.objects.annotate(
            avg_rating=Avg('review_ratings__rating'),
            rating_count=Count('review_ratings')
        ).filter(
            avg_rating__gt=4.5,
            rating_count__gt=0
        ).order_by('-avg_rating')[:limit]


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="review_ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.TextField(max_length=500, blank=True)
    rating = models.PositiveSmallIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} reviewed {self.product.name} with {self.rating} stars"
