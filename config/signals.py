from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from shop.models import Product, ReviewRating
from cart.models import Cart, CartItem
from favourite.models import Favourite, FavouriteProduct
from users.models import User
from main.tasks import log_task


# Products
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_product_cache(sender, instance, **kwargs):
    cache.delete(f'product_{instance.id}')
    log_task(f"Cache for Product {instance.id} has been deleted", 'debug')

# Cart
@receiver(post_save, sender=CartItem)
@receiver(post_delete, sender=CartItem)
def update_cart_cache(sender, instance, **kwargs):
    user_id = instance.cart.user.id
    cache.delete(f'cart_{user_id}')
    log_task(f"Cache for Cart Item of user {user_id} has been deleted", 'debug')

@receiver(post_save, sender=Cart)
@receiver(post_delete, sender=Cart)
def update_cart_cache_full(sender, instance, **kwargs):
    cache.delete(f'cart_{instance.user.id}')
    log_task(f"Cache for Cart of user {instance.user.id} has been deleted", 'debug')

# Favourites
@receiver(post_save, sender=FavouriteProduct)
@receiver(post_delete, sender=FavouriteProduct)
def update_favourite_cache(sender, instance, **kwargs):
    user_id = instance.favourite.user.id
    cache.delete(f'favorite_{user_id}')
    log_task(f"Cache for Favourite item of user {user_id} has been deleted", 'debug')

@receiver(post_save, sender=Favourite)
@receiver(post_delete, sender=Favourite)
def update_favourite_cache_full(sender, instance, **kwargs):
    cache.delete(f'favorite_{instance.user.id}')
    log_task(f"Cache for Favourite of user {instance.user.id} has been deleted", 'debug')

# Reviews
@receiver(post_save, sender=ReviewRating)
@receiver(post_delete, sender=ReviewRating)
def update_review_cache(sender, instance, **kwargs):
    product_id = instance.product.id
    cache.delete(f'product_reviews_{product_id}')  # Удаляем кэш для отзывов продукта
    log_task(f"Cache for Review of product {product_id} has been deleted", 'debug')

# User profile
@receiver(post_save, sender=User)
@receiver(post_delete, sender=User)
def update_user_cache(sender, instance, **kwargs):
    cache.delete(f'user_profile_{instance.id}')
    log_task(f"Cache for Profile of user {instance.id} has been deleted", 'debug')


# Delivery Policy
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_delivery_policy(sender, instance, **kwargs):
    cache.delete('delivery_policy')  
    log_task(f"Cache for Delivery Policy page has been deleted", 'debug')

# Terms
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_terms(sender, instance, **kwargs):
    cache.delete('terms')  
    log_task(f"Cache for Terms page has been deleted", 'debug')

# Privacy Policy
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_privacy_policy(sender, instance, **kwargs):
    cache.delete('privacy_policy') 
    log_task(f"Cache for Privacy Policy page has been deleted", 'debug')

# Refund
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_refund_policy(sender, instance, **kwargs):
    cache.delete('refund_policy')
    log_task(f"Cache for Refund Policy page has been deleted", 'debug')

# About Us
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_about_us(sender, instance, **kwargs):
    cache.delete('about_us')
    log_task(f"Cache for About Us page has been deleted", 'debug')

# Contact Us
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_contact_us(sender, instance, **kwargs):
    cache.delete('contact_us')
    log_task(f"Cache for Contact Us page has been deleted", 'debug')

# Index
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_cache_index(sender, instance, **kwargs):
    cache.delete('index') 
    log_task(f"Cache for Index page has been deleted", 'debug')