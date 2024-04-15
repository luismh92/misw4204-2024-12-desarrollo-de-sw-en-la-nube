""" User Model """
from app.models.database import Base
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, Field

class User(Base):
    """ This class represents the users table in the database. """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    password1 = Column(String)
    password2 = Column(String)
    email = Column(String, index=True, unique=True)
    is_active = Column(Boolean, default=True)


class UsersCreate(BaseModel):
    """ This class represents the model for creating a new user. """
    email: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=100)
    password1: str = Field(min_length=1, max_length=100)
    password2: str = Field(min_length=1, max_length=100)
