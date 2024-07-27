from django.db import models
import random


class Category(models.Model):
    name = models.CharField(verbose_name="name", max_length=30)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    @property
    def get_first_12_random_products(self):
        products = list(Product.objects.all())
        random_products = random.sample(products, min(len(products), 12))
        return random_products


class Product(models.Model):
    image = models.ImageField(verbose_name="image", upload_to="products")
    name = models.CharField(verbose_name="name", max_length=50)
    description = models.TextField(verbose_name="description")
    price = models.DecimalField(verbose_name="price", max_digits=7, decimal_places=2, default=1, blank=True)
    discount = models.SmallIntegerField(verbose_name="discount", default=0, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    @property
    def price_with_discount(self):
        return self.price - (self.price * self.discount / 100)
