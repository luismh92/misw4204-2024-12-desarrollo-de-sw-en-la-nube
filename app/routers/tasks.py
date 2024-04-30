""" Módulo de tareas de edición de video. """
import uuid
import pathlib
import os
import logging
from typing import Annotated
from app.workers.worker import convertir_video
from app.models import task, database, gcp
from app.routers.auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

router = APIRouter(
    prefix="/api/tasks",
)
UserDependency = Annotated[dict, Depends(get_current_user)]

INPUT_PATH_RESOURCES = os.environ.get("INPUT_PATH_RESOURCES", "./resources/")
GCP_BUCKET = os.environ.get("GCP_BUCKET", 'desarrollo-sw-en-la-nube-miso4203')


@router.get("",  tags=["tasks"])
def read_tasks(user: UserDependency, db: Session = Depends(database.get_db)):
    """ Permite recuperar todas las tareas de edición de un usuario autorizado en la aplicación. """
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed .')
    object_tasks = db.query(task.Task).all()
    return object_tasks


@router.post("",  tags=["tasks"])
def crear_tasks(user: UserDependency,
                file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    """ Permite crear una nueva tarea de edición de video. El usuario requiere autorización."""
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    if not file:
        return {"message": "No upload file sent"}
    else:
        task_id = uuid.uuid4()
        try:
            contents = file.file.read()
            file_name = pathlib.Path(file.filename).suffix
            def get_path(method='input'):
                return f"{INPUT_PATH_RESOURCES}{method}/{task_id}{file_name}"

            file_path = get_path()

            with open(file_path, 'wb') as f:
                f.write(contents)
            logging.info("File %s uploaded successfully", file.filename)

        except Exception as e:
            print("error uploading file: ", str(e))
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()

        logging.info("Task %s created", task_id)
        gcp_path = f'resources/input/{task_id}{file_name}'
        gcp.upload_blob(GCP_BUCKET, file_path, gcp_path)
        logging.info("Task %s sent to worker", task_id)
        convertir_video.delay(task_id, GCP_BUCKET, gcp_path)
        new_task = task.Task(task_id=task_id, status='uploaded', input_path=gcp_path)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return {"fileName": file.filename, "task_id": task_id}


@router.get("/{id_task}",  tags=["tasks"])
def read_task_by_id(user: UserDependency, id_task: str, db: Session = Depends(database.get_db)):
    """ Permite recuperar la información de una tarea en la aplicación. El usuario requiere
autorización. """
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed.')

    object_task = db.query(task.Task).filter(
        task.Task.task_id == id_task).one_or_none()
    result = {
        "id": object_task.id,
        "task_id": object_task.task_id,
        "status": object_task.status,
        "input_path": object_task.input_path,
        "time_stamp": object_task.time_stamp
    }
    return result


@router.put("/to-processed/{id_task}",  tags=["tasks"])
def update_task_to_processed(id_task: str, db: Session = Depends(database.get_db)):
    """ Permite recuperar la información de una tarea en la aplicación. El usuario requiere
autorización. """
    db_task = db.query(task.Task).filter(
        task.Task.task_id == id_task).one_or_none()
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
def delete_task_by_id(user: UserDependency, id_task: str, db: Session = Depends(database.get_db)):
    """ Permite eliminar una tarea en la aplicación. El usuario requiere autorización. """
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed.')

    db_task = db.query(task.Task).filter(
        task.Task.task_id == id_task).one_or_none()
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
