from django.db.models.signals import post_save, post_delete
from apps.cart.models import Cart, CartItem
from django.dispatch import receiver
from django.core.cache import cache
from core.tasks import log_task


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