""" Celery worker to create tasks """
import os
import time
import subprocess
from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="convertir_video")
def convertir_video(file_path, output_path):
    """ Create a task that takes some time to complete"""
    subprocess.run(f'ffmpeg -t 30 -r 10 -i {file_path} -aspect 16:10 -r ntsc '+str(output_path), shell=True)
    return True
