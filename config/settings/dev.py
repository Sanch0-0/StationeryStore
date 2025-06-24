from django.conf import settings

ALLOWED_HOSTS = ['*']
MEDIA_URL = '/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': settings.BASE_DIR / 'db.sqlite3',
    }
}
