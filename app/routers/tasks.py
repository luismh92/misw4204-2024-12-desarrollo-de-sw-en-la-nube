""" Módulo de tareas de edición de video. """
from fastapi import APIRouter, UploadFile, File
from app.workers.worker import convertir_video
from uuid import UUID
from celery.result import AsyncResult
import uuid
import pathlib
router = APIRouter(
    prefix="/api/tasks",
)


fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("",  tags=["tasks"])
def read_tasks():
    """ Permite recuperar todas las tareas de edición de un usuario autorizado en la aplicación. """
    return fake_items_db


@router.post("",  tags=["tasks"])
def crear_tasks(file: UploadFile = File(...)):
    """ Permite crear una nueva tarea de edición de video. El usuario requiere autorización."""
    print(file)
    if not file:
        return {"message": "No upload file sent"}
    else:
        try:
            contents = file.file.read()
            task_id = uuid.uuid4()

            def get_path(method='input'):
                return f"./resources/{method}/{task_id}{pathlib.Path(file.filename).suffix}"

            file_path = get_path()
            with open(file_path, 'wb') as f:
                f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()
        output_path = get_path('output')
        task = convertir_video.delay(file_path, output_path)
        print(file_path)
        # ffmpeg.input(file_path).trim(start=0, duration=30).filter(
        #     'fps', fps=25, round='up').output(output_path).run()
        return {"fileName": file.filename, "task_id": task.id}


@router.get("/{id_task}",  tags=["tasks"])
def read_task_by_id(id_task: str):
    """ Permite recuperar la información de una tarea en la aplicación. El usuario requiere
autorización. """
    task_result = AsyncResult(id_task)
    result = {
        "task_id": id_task,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result


@router.delete("/{id_task}",  tags=["tasks"])
def delete_task_by_id(id_task: str):
    """ Permite eliminar una tarea en la aplicación. El usuario requiere autorización. """
    return fake_items_db
