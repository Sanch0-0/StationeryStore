from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from shop.models import Product, ReviewRating
from cart.models import Cart, CartItem
from favourite.models import Favourite, FavouriteProduct
from users.models import User

def clear_view_cache(view_name, *args):
    """Delete view cache by view's name and arguments"""
    key = make_template_fragment_key(view_name, args)
    cache.delete(key)

# Products
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_product_cache(sender, instance, **kwargs):
    cache.delete(f'product_{instance.id}')

# Cart
@receiver(post_save, sender=CartItem)
@receiver(post_delete, sender=CartItem)
def update_cart_cache(sender, instance, **kwargs):
    user_id = instance.cart.user.id
    cache.delete(f'cart_{user_id}')

@receiver(post_save, sender=Cart)
@receiver(post_delete, sender=Cart)
def update_cart_cache_full(sender, instance, **kwargs):
    cache.delete(f'cart_{instance.user.id}')

# Favourites
@receiver(post_save, sender=FavouriteProduct)
@receiver(post_delete, sender=FavouriteProduct)
def update_favourite_cache(sender, instance, **kwargs):
    user_id = instance.favourite.user.id
    cache.delete(f'favorite_{user_id}')

@receiver(post_save, sender=Favourite)
@receiver(post_delete, sender=Favourite)
def update_favourite_cache_full(sender, instance, **kwargs):
    cache.delete(f'favorite_{instance.user.id}')

# Reviews
@receiver(post_save, sender=ReviewRating)
@receiver(post_delete, sender=ReviewRating)
def update_review_cache(sender, instance, **kwargs):
    product_id = instance.product.id
    cache.delete(f'product_reviews_{product_id}')

# User profile
@receiver(post_save, sender=User)
@receiver(post_delete, sender=User)
def update_user_cache(sender, instance, **kwargs):
    cache.delete(f'user_profile_{instance.id}')


# Delivery Policy
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_delivery_policy(sender, instance, **kwargs):
    clear_view_cache('delivery_policy')  

# Terms
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_terms(sender, instance, **kwargs):
    clear_view_cache('terms')  

# Privacy Policy
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_privacy_policy(sender, instance, **kwargs):
    clear_view_cache('privacy_policy')  

# Refund
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_refund_policy(sender, instance, **kwargs):
    clear_view_cache('refund_policy')

# About Us
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_about_us(sender, instance, **kwargs):
    clear_view_cache('about_us')

# Indes
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_index(sender, instance, **kwargs):
    clear_view_cache('index')
