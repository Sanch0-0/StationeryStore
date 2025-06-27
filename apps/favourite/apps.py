from django.apps import AppConfig


class FavouriteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.favourite'

    def ready(self):
        from . import signals