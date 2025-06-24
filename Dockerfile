# Базовый образ Python
FROM python:3.12-slim

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . /app/

# Даем права на выполнение entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Открываем порт (не обязательно, но полезно)
EXPOSE 8888

# Устанавливаем entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

