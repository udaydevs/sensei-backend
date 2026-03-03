"""User Model"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text
from app.core.database import Base

class Users(Base):
    """
    DB model for user details
    """
    __tablename__= 'Users'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    email = Column(String,nullable=False, unique=True)
    password = Column(String, nullable=False, unique = True)
    is_active = Column(Boolean, server_default=text('false'))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
