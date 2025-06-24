#!/bin/sh

mkdir -p /logs
chmod -R 777 /logs

echo "🚀 Применение миграций..."
python manage.py migrate --noinput

echo "📦 Сбор статики..."
python manage.py collectstatic --noinput

echo "🔥 Запуск Gunicorn..."
exec gunicorn main.wsgi:application \
    --bind unix:/gunicorn/sockets/gunicorn.sock \
    --workers 7 \
    --timeout 60 \
    --access-logfile /logs/django.log

