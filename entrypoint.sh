#!/bin/sh

mkdir -p /logs
chmod -R 777 /logs

echo "🔄 Применяем миграции..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "📦 Собираем статику..."
python manage.py collectstatic --noinput

echo "👤 Создаем суперюзера, если его нет..."
python manage.py shell <<EOF
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('${SUPERUSER_NAME}', '${SUPERUSER_EMAIL}', '${SUPERUSER_PASSWORD}')
    print("✅ Суперюзер создан.")
else:
    print("⚠️ Суперюзер уже существует.")
EOF

echo "🔥 Запускаем Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind unix:/gunicorn/sockets/gunicorn.sock \
    --workers 7 \
    --timeout 60 \
    --access-logfile /logs/django.log