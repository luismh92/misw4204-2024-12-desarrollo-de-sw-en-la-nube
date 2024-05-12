""" Módulo que contiene las tareas de Celery. """
import os
import subprocess
import requests as req
from celery import Celery
from app.models import gcp
celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

@celery.task(name="convertir_video")
def convertir_video(task_id, bucket_name, gcp_path):
    """ Convierte un video a un formato específico. """
    file_name_download = f'./resources/output/{task_id}_temp.mp4'
    gcp.download_blob(bucket_name, gcp_path, file_name_download)
    # URL del logo
    logo_url = "https://www.sportsbusinessjournal.com/-/media/Sporttechie/2016/10/21/Screen-Shot-2016-10-19-at-9_29_33-AM.ashx"
    logo_path = "/tmp/idrl_logo.png"  # Cambiar según la estructura de carpetas del servidor
    output_path = gcp_path.replace("input", "output")
    # Descargar el logo si no existe
    if not os.path.exists(logo_path):
        response = req.get(logo_url, allow_redirects=True)
        response.raise_for_status()  # Asegurarse de que la descarga fue exitosa
        with open(logo_path, 'wb') as f:
            f.write(response.content)

    # Primer paso: Recortar y escalar el video
    temp_video_path = "/tmp/temp_video.mp4"  # Cambiar según la estructura de carpetas del servidor
    subprocess.run(
        [
            'ffmpeg', '-i', file_name_download, '-t', '20', '-vf', 'scale=1920x1080,setdar=16/9', 
            '-c:v', 'libx264', '-c:a', 'copy', temp_video_path
        ],
        check=True
    )

    # Segundo paso: Añadir logo al principio y al final
    subprocess.run(
        [
            'ffmpeg', '-i', temp_video_path, '-i', logo_path,
            '-filter_complex',
            "[0:v][1:v]overlay=W-w-10:H-h-10:enable='between(t,0,2)'[temp1];[temp1][1:v]overlay=W-w-10:H-h-10:enable='between(t,18,20)'",
            '-c:v', 'libx264', '-c:a', 'copy', output_path
        ],
        check=True
    )

    gcp.upload_blob(bucket_name, output_path, output_path)
    # Eliminar el archivo de video temporal
    os.remove(temp_video_path)
    os.remove(file_name_download)
    # Actualizar el estado de la tarea en el backend
    req.put(f'{BACKEND_URL}/api/tasks/to-processed/{task_id}')
    return True
