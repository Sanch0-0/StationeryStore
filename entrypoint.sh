#!/bin/sh

mkdir -p /logs
chmod -R 777 /logs

if [ "$DJANGO_ROLE" = "web" ]; then
  echo "🔄 Применяем миграции..."
  python manage.py makemigrations --noinput
  python manage.py migrate --noinput

  echo "📦 Собираем статику..."
  python manage.py collectstatic --noinput

  echo "👤 Создаем суперюзера..."
  PYTHONPATH=/app python core/create_superuser.py # для нахождения config/

  echo "🔥 Запускаем Gunicorn..."
  exec gunicorn config.wsgi:application \
      --bind unix:/gunicorn/sockets/gunicorn.sock \
      --workers 7 \
      --timeout 60 \
      --access-logfile /logs/django.log

elif [ "$DJANGO_ROLE" = "celery" ]; then
  echo "🐇 Запускаем Celery worker..."
  exec celery -A config worker --loglevel=info --uid=nobody

# elif [ "$DJANGO_ROLE" = "beat" ]; then
#   echo "📅 Запускаем Celery Beat..."
#   exec celery -A config beat --loglevel=info

else
  echo "❌ DJANGO_ROLE не указан или неизвестен: '$DJANGO_ROLE'"
  exit 1
fi