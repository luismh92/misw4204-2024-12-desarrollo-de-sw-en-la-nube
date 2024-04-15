""" Módulo de tareas de edición de video. """
import uuid
import pathlib
from fastapi import APIRouter, UploadFile, File, Depends
from app.workers.worker import convertir_video
from celery.result import AsyncResult
from app.models import task, database
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/tasks",
)


@router.get("",  tags=["tasks"])
def read_tasks(db: Session = Depends(database.get_db)):
    """ Permite recuperar todas las tareas de edición de un usuario autorizado en la aplicación. """
    object_tasks = db.query(task.Task).all()
    return object_tasks


@router.post("",  tags=["tasks"])
def crear_tasks(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    """ Permite crear una nueva tarea de edición de video. El usuario requiere autorización."""
    if not file:
        return {"message": "No upload file sent"}
    else:
        task_id = uuid.uuid4()
        try:
            contents = file.file.read()
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
        convertir_video.delay(task_id, file_path, output_path)
        new_task = task.Task(task_id = task_id, status = 'uploaded')
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return {"fileName": file.filename, "task_id": task_id}


@router.get("/{id_task}",  tags=["tasks"])
def read_task_by_id(id_task: str, db: Session = Depends(database.get_db)):
    """ Permite recuperar la información de una tarea en la aplicación. El usuario requiere
autorización. """
    object_task = db.query(task.Task).filter(task.Task.task_id == id_task).one_or_none()
    result = {
        "id": object_task.id,
        "task_id": object_task.task_id,
        "status": object_task.status,
        "time_stamp": object_task.time_stamp
    }
    return result


@router.put("/to-processed/{id_task}",  tags=["tasks"])
def update_task_to_processed(id_task: str, db: Session = Depends(database.get_db)):
    """ Permite recuperar la información de una tarea en la aplicación. El usuario requiere
autorización. """
    db_task = db.query(task.Task).filter(task.Task.task_id == id_task).one_or_none()
    if db_task is None:
        return {
            "task_id": id_task,
            "message": "Task not found"
        }

    db_task.status = 'processed'
    db.commit()
    db.refresh(db_task)
    result = {
        "task_id": id_task
    }
    return result


@router.delete("/{id_task}",  tags=["tasks"])
def delete_task_by_id(id_task: str, db: Session = Depends(database.get_db)):
    """ Permite eliminar una tarea en la aplicación. El usuario requiere autorización. """
    db_task = db.query(task.Task).filter(task.Task.task_id == id_task).one_or_none()
    if db_task is None:
        return {
            "task_id": id_task,
            "message": "Task not found"
        }

    db.delete(db_task)
    db.commit()
    result = {
        "task_id": id_task,
        "message": "Task deleted"
    }
    return result
