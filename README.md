🎯 Идеальный вариант:

    web-app (Django + Gunicorn)
    postgres (База данных)
    nginx (Reverse Proxy)
    redis (Брокер и кеш)
    celery-worker (Обработчик задач)
    celery-beat (Если есть периодические задачи)

Elasticsearch и Logstash на рассмотрение
не забыть про Flower


<!-- gunicorn.socket -->
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target


<!-- gunicorn.service -->
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=alex
Group=alex
WorkingDirectory=/home/alex/Python_course/Django/StationeryStore
ExecStart=/home/alex/Python_course/Django/StationeryStore/venv/bin/gunicorn --config /home/alex/Python_course/Django/StationeryStore/gunicorn.conf main.wsgi:application

[Install]
WantedBy=multi-user.target
