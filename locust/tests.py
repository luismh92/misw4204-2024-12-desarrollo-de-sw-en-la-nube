import os
from locust import HttpUser, task, between
import requests

class VideoUploadUser(HttpUser):
    wait_time = between(1, 10)  # Tiempo de espera entre tareas

    @task
    def upload_video(self):
        url = 'http://localhost:8004/api/tasks'
        video_path = os.path.join(os.path.dirname(__file__), 'video1234test.mp4')
        files = {'file': open(video_path, 'rb')}
        headers = {'accept': 'application/json'}

        try:
            response = requests.post(url, files=files, headers=headers)
            if response.status_code == 200:
                print("¡El video se subió correctamente!")
                self.environment.runner.stats.log_request(method="POST", name="/api/tasks", response_time=response.elapsed.total_seconds(), content_length=len(response.content))
            else:
                print("Error al subir el video. Código de respuesta:", response.status_code)
                print("Contenido de la respuesta:", response.content)
        except Exception as e:
            print("Error al subir el video:", e)
