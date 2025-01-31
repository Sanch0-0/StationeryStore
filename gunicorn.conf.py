import multiprocessing
import os
    
access_logfile = '/home/alex/Python_course/Django/StationeryStore/logs/django.log'
workers = multiprocessing.cpu_count() * 2 + 1
bind = 'unix:/run/gunicorn.sock'
timeout = 30

# bind = "0.0.0.0:8888"
