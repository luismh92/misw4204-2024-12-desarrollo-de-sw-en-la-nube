""" A simple worker that listens for messages on a Pub/Sub subscription. """
import os
import json
import subprocess
import requests as req
from workers import gcp
from google.cloud import pubsub_v1
from fastapi import FastAPI

app = FastAPI()

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
path_absolute = os.path.abspath("app/models/credentials.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=path_absolute
project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'desarrollo-de-sw-en-la-nube-04')
subscription_id = "desarrollo-de-software-en-la-nube-sub"


def get_message():
    """ Listens for messages on a Pub/Sub subscription. """
    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        """ Receives a pub/sub message. """
        response = json.loads((message.data).decode())
        print(response["task_id"])
        print(response["gcp_bucket"])
        print(response["gcp_path"])
        convertir_video(response["task_id"], response["gcp_bucket"], response["gcp_path"])
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Keep the script running to continue receiving messages
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()


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

get_message()
