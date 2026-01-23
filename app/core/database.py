"""Database engine are defined here"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


engine = create_engine(str(settings.SQLALCHEMY_POSTGRES_URL))

SessionLocal = sessionmaker(autoflush=True, autocommit = False, bind=engine)

Base = declarative_base()

def get_db():
    """It will create a database session and after execution the session will get close"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbDependency = Annotated[Session, Depends(get_db)]
