"""Database engine are defined here"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DB_URL = "postgresql://postgres.rcfxkyzfekabtctcldtf:l7zuW7ErkwjmwF17@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

engine = create_engine(DB_URL)

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
