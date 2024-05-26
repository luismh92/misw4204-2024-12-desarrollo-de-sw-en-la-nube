""" A simple worker that listens for messages on a Pub/Sub subscription. """
import os
import json
import subprocess
import requests as req
from workers import gcp
from google.cloud import pubsub_v1
from fastapi import FastAPI
import uuid
import time
from fastapi import FastAPI, HTTPException
import base64
from typing import Optional, Dict, Any
from pydantic import BaseModel

app = FastAPI()
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
path_absolute = os.path.abspath("workers/credentials.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=path_absolute
project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'desarrollo-de-sw-en-la-nube-04')
subscription_id = "desarrollo-de-software-en-la-nube-sub"

GCP_BUCKET = os.environ.get("GCP_BUCKET", 'desarrollo-sw-en-la-nube-miso4203')

class PubSubMessage(BaseModel):
    data: Optional[str]
    attributes: Optional[Dict[str, Any]]

class Envelope(BaseModel):
    message: Optional[PubSubMessage]
    subscription: str

@app.post("/")
async def index(envelope: Envelope):
    """Receive and parse Pub/Sub messages."""
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        raise HTTPException(status_code=400, detail=msg)

    if not isinstance(envelope.dict(), dict) or "message" not in envelope.dict():
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        raise HTTPException(status_code=400, detail=msg)

    print(f"envelope value: {envelope}!")
    pubsub_message = envelope.message

    response = "pubsub_message"
    if isinstance(pubsub_message.dict(), dict) and "data" in pubsub_message.dict():
        response = base64.b64decode(pubsub_message.data).decode("utf-8").strip()
        get_message(response)
    print(f"pubsub_message value: {response}!")

    return {"message": "Message processed"}


def get_message(response):
    """ Listens for messages on a Pub/Sub subscription. """
    print("response:")
    print(response)
    response = json.loads(response)
    print(response["task_id"])
    print(response["gcp_path"])
    convertir_video(response["task_id"], GCP_BUCKET, response["gcp_path"])

    print(f"Listening for messages on {response}..\n")

    # subscriber = pubsub_v1.SubscriberClient()
    # # The `subscription_path` method creates a fully qualified identifier
    # # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    # subscription_path = subscriber.subscription_path(project_id, subscription_id)

    # def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    #     """ Receives a pub/sub message. """
    #     response = json.loads((message.data).decode())
    #     print(response["task_id"])
    #     print(response["gcp_path"])
    #     convertir_video(response["task_id"], GCP_BUCKET, response["gcp_path"])
    #     message.ack()

    # streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    # print(f"Listening for messages on {subscription_path}..\n")

    # # Keep the script running to continue receiving messages
    # try:
    #     streaming_pull_future.result()
    # except KeyboardInterrupt:
    #     streaming_pull_future.cancel()


def convertir_video(task_id, bucket_name, gcp_path):
    """ Convierte un video a un formato específico. """
    file_name_download = f'./resources/output/{task_id}_temp.mp4'
    while not gcp.blob_exists(bucket_name, gcp_path):
        time.sleep(5)  # Esperar 5 segundos y volver a intentar
        
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
    temp_video_path = f"/tmp/{uuid.uuid4()}.mp4"  # Cambiar según la estructura de carpetas del servidor
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
