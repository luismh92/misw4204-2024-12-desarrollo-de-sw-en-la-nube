import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_HOST_URL = os.environ.get("DB_HOST_URL", "127.0.0.1:5433")
SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://postgres:123456@{DB_HOST_URL}/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """ Crea una nueva sesión de base de datos para la solicitud."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
