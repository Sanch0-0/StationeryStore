from django.db.models.signals import post_save, post_delete
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.core.cache import cache


User = get_user_model


@receiver(post_save, sender=User)
@receiver(post_delete, sender=User)
def update_user_cache(sender, instance, **kwargs):
    cache.delete(f'user_profile_{instance.id}')
    log_task(f"Cache for Profile of user {instance.id} has been deleted", 'debug')