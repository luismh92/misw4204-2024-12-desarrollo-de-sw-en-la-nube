""" Módulo de tareas de edición de video. """
import uuid
import pathlib
from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.workers.worker import convertir_video
from app.models import task, database
from app.routers.auth import get_current_user
from sqlalchemy.orm import Session
import os
import logging
router = APIRouter(
    prefix="/api/tasks",
)
UserDependency = Annotated[dict, Depends(get_current_user)]

INPUT_PATH_RESOURCES = os.environ.get("INPUT_PATH_RESOURCES", "./resources/")
OUTPUT_PATH_RESOURCES = os.environ.get("OUTPUT_PATH_RESOURCES", "./resources/")


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
            def get_path(method='input'):
                return f"{INPUT_PATH_RESOURCES}{method}/{task_id}{pathlib.Path(file.filename).suffix}"

            def get_path_ouput():
                method = 'output'
                return f"{OUTPUT_PATH_RESOURCES}{method}/{task_id}{pathlib.Path(file.filename).suffix}"
            

            file_path = get_path()
            
            with open(file_path, 'wb') as f:
                f.write(contents)
            logging.info(f"File {file.filename} uploaded successfully")
        except Exception as e:
            print("error uploading file: ", str(e))
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()
        output_path = get_path_ouput()
        logging.info(f"Task {task_id} created")
        convertir_video.delay(task_id, file_path, output_path)
        logging.info(f"Task {task_id} sent to worker")
        new_task = task.Task(task_id = task_id, status = 'uploaded')
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
def delete_task_by_id(user: UserDependency, id_task: str, db: Session = Depends(database.get_db)):
    """ Permite eliminar una tarea en la aplicación. El usuario requiere autorización. """
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed.')

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
