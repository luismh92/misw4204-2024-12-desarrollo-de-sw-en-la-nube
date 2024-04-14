""" Celery worker to create tasks """
import os
import subprocess
import requests as req
from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

@celery.task(name="convertir_video")
def convertir_video(task_id, file_path, output_path):
    """ Create a task that takes some time to complete"""
    subprocess.run(f'ffmpeg -t 20 -r 10 -i {file_path} -aspect 16:10 -r ntsc '+str(output_path), shell=True)
    req.put(f'{BACKEND_URL}/api/tasks/to-processed/{task_id}')
    return True
