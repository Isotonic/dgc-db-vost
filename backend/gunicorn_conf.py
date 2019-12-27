# Credit to Sebastián Ramírez
# https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/master/python3.6/gunicorn_conf.py

import os
import json
import psutil

workers_per_core_str = os.getenv('WORKERS_PER_CORE', '2')
web_concurrency_str = os.getenv('WEB_CONCURRENCY', None)
use_loglevel = os.getenv('LOG_LEVEL', 'errors')

cores = psutil.cpu_count(logical = False)
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2) + 1

# Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
bind = '0.0.0.0:5000'
keepalive = 120
errorlog = '-'
worker_tmp_dir = '/dev/shm'

# For debugging and testing
log_data = {
    'loglevel': loglevel,
    'worker': workers,
    'bind': bind,
    # Additional, non-gunicorn variables
    'workers_per_core': workers_per_core
}
print(json.dumps(log_data))