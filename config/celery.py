from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from main.tasks import log_task


# Устанавливаем модуль настроек Django по умолчанию для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('config')

# Загружаем конфигурацию из settings.py с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    log_task(f'Request: {self.request!r}', 'debug')
