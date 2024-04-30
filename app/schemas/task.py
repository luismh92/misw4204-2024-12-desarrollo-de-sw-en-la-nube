from pydantic import BaseModel


class TaskBase(BaseModel):
    """ Task Base Schema """
    status: str
    task_id: str
    input_path: str

    class Config:
        """ORM Mode"""
        orm_mode = True


class CreateTask(TaskBase):
    """ Create Task Schema """
    class Config:
        """ORM Mode"""
        orm_mode = True
        