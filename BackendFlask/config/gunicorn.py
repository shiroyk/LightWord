import os

if not os.path.exists('logs'):
    os.mkdir('logs')

workers = 4
threads = 2
bind = '0.0.0.0:5000'
worker_class = 'gevent'
worker_connections = 2000
loglevel = 'info'
