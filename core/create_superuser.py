# scripts/create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("SUPERUSER_NAME")
email = os.environ.get("SUPERUSER_EMAIL")
password = os.environ.get("SUPERUSER_PASSWORD")

if not all([username, email, password]):
    print("❌ SUPERUSER_* env variables not set!")
    exit(1)

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Superuser created.")
else:
    print("⚠️ Superuser already exists.")
