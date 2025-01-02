from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from shop.models import Product
from cart.models import Cart
from favourite.models import Favourite

@receiver(post_save, sender=Product)
def update_product_cache(sender, instance, **kwargs):
    # Очищаем кэш для страницы товара
    cache.delete(f'product_{instance.id}')
    # Если нужно, кэшируем товар заново
    cache.set(f'product_{instance.id}', instance)

@receiver(post_delete, sender=Product)
def delete_product_cache(sender, instance, **kwargs):
    # Удаляем кэш для удаленного товара
    cache.delete(f'product_{instance.id}')

@receiver(post_save, sender=Cart)
def update_cart_cache(sender, instance, **kwargs):
    # Очищаем кэш для корзины пользователя
    cache.delete(f'cart_{instance.user.id}')
    # Если нужно, кэшируем корзину заново
    cache.set(f'cart_{instance.user.id}', instance)

@receiver(post_delete, sender=Cart)
def delete_cart_cache(sender, instance, **kwargs):
    # Удаляем кэш для удаленной корзины
    cache.delete(f'cart_{instance.user.id}')

@receiver(post_save, sender=Favorite)
def update_favorite_cache(sender, instance, **kwargs):
    # Очищаем кэш для списка любимых товаров пользователя
    cache.delete(f'favorite_{instance.user.id}')
    # Если нужно, кэшируем список заново
    cache.set(f'favorite_{instance.user.id}', instance)

@receiver(post_delete, sender=Favorite)
def delete_favorite_cache(sender, instance, **kwargs):
    # Удаляем кэш для удаленного списка любимых товаров
    cache.delete(f'favorite_{instance.user.id}')
