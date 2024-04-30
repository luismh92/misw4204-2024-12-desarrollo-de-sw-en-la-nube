""" Task Model """
from app.models.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import TEXT

class Task(Base):
    """ Task Model """
    __tablename__ = "tasks"
    id = Column(Integer,primary_key=True,nullable=False)
    status = Column(String,nullable=False)
    time_stamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    task_id = Column(String,nullable=False)
    input_path = Column(TEXT,nullable=True)
    output_path = Column(TEXT,nullable=True)
