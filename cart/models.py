from django.db import models
from shop.models import Product

class Cart(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="carts")
    products = models.ManyToManyField(Product, through='CartItem')
    created_at = models.DateTimeField(verbose_name="creation date", auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"

    @property
    def products_count(self) -> int:
        return self.products.count()

    def total_price(self):
        total = sum(
            item.product.price_with_discount * item.quantity for item in self.cart_items.all()
        )
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Cart {self.cart.id}"

