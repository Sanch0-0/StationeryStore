from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from shop.models import Product, ReviewRating
from cart.models import Cart, CartItem
from favourite.models import Favourite, FavouriteProduct
from users.models import User
from shop.models import Category


#? API
# Update the product cache on creation or update
@receiver(post_save, sender=Product)
def update_product_cache(sender, instance, created, **kwargs):
    cache_key = f"product_{instance.id}"
    # If the product is created or updated, update the cache
    if created or not cache.get(cache_key):
        cache.set(cache_key, instance, timeout=3600) # 1 hour

# Delete the product cache when the product is deleted
@receiver(post_delete, sender=Product)
def delete_product_cache(sender, instance, **kwargs):
    cache_key = f"product_{instance.id}"
    cache.delete(cache_key)

# Update the cart cache on adding or updating a cart item
@receiver(post_save, sender=CartItem)
def update_cart_cache(sender, instance, created, **kwargs):
    cache_key = f"cart_{instance.cart.id}"
    cache.set(cache_key, instance.cart, timeout=900) # 15 mins

# Delete the cart cache when a cart item is deleted
@receiver(post_delete, sender=CartItem)
def delete_cart_cache(sender, instance, **kwargs):
    cache_key = f"cart_{instance.cart.id}"
    cache.delete(cache_key)

# Update the favourite cache on adding or updating a favourite product
@receiver(post_save, sender=FavouriteProduct)
def update_favourite_cache(sender, instance, created, **kwargs):
    cache_key = f"favourite_{instance.favourite.id}"
    cache.set(cache_key, instance.favourite, timeout=900)

# Delete the favourite cache when a favourite product is deleted
@receiver(post_delete, sender=FavouriteProduct)
def delete_favourite_cache(sender, instance, **kwargs):
    cache_key = f"favourite_{instance.favourite.id}"
    cache.delete(cache_key) 

# Update the review cache on adding or updating a review
@receiver(post_save, sender=ReviewRating)
def update_review_cache(sender, instance, created, **kwargs):
    cache_key = f"review_{instance.product.id}"
    cache.set(cache_key, instance.product.reviews.all(), timeout=1800) # 30 mins

# Delete the review cache when a review is deleted
@receiver(post_delete, sender=ReviewRating)
def delete_review_cache(sender, instance, **kwargs):
    cache_key = f"review_{instance.product.id}"
    cache.delete(cache_key)

# Update the category cache on creation or update
@receiver(post_save, sender=Category)
def update_category_cache(sender, instance, created, **kwargs):
    cache_key = f"category_{instance.id}"
    cache.set(cache_key, instance, timeout=43200) # 12 hours

# Delete the category cache when the category is deleted
@receiver(post_delete, sender=Category)
def delete_category_cache(sender, instance, **kwargs):
    cache_key = f"category_{instance.id}"
    cache.delete(cache_key) 

# Delete the favourite cache when a user's favourite is deleted
@receiver(post_delete, sender=Favourite)
def delete_favourite_user_cache(sender, instance, **kwargs):
    cache_key = f"favourite_{instance.id}"
    cache.delete(cache_key)

# Delete the cart cache when a user's cart is deleted
@receiver(post_delete, sender=Cart)
def delete_cart_user_cache(sender, instance, **kwargs):
    cache_key = f"cart_{instance.id}"
    cache.delete(cache_key)