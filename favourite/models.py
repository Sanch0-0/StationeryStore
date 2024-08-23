from django.db import models
from shop.models import Product

class Favourite(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="favourite")
    products = models.ManyToManyField(Product, through='FavouriteProduct')
    created_at = models.DateTimeField(verbose_name="creation date", auto_now_add=True)

    def __str__(self):
        return f"Favourite {self.id} for {self.user.username}"

    @property
    def products_count(self) -> int:
        return self.products.count()

    def total_price(self):
        total = sum(
            item.product.price_with_discount * item.quantity for item in self.favourite_items.all()
        )
        return total

class FavouriteProduct(models.Model):
    favourite = models.ForeignKey(Favourite, on_delete=models.CASCADE, related_name='favourite_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Favourite {self.favourite.id}"
