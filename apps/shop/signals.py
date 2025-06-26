from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from core.tasks import log_task
from apps.shop.models import *


# Products
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_product_cache(sender, instance, **kwargs):
    cache.delete(f'product_{instance.id}')
    log_task(f"Cache for Product {instance.id} has been deleted", 'debug')

# Reviews
@receiver(post_save, sender=ReviewRating)
@receiver(post_delete, sender=ReviewRating)
def update_review_cache(sender, instance, **kwargs):
    product_id = instance.product.id
    cache.delete(f'product_reviews_{product_id}')  # Удаляем кэш для отзывов продукта
    log_task(f"Cache for Review of product {product_id} has been deleted", 'debug')

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