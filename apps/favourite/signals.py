from apps.favourite.models import Favourite, FavouriteProduct
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from core.tasks import log_task


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