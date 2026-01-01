"""User Model"""
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text
from pydantic import EmailStr
from app.core.database import Base


class Register(BaseModel):
    """
    Model for authentication
    """
    name : str
    email: EmailStr
    password : str
class Login(BaseModel):
    """Login Model"""
    email : EmailStr
    password : str

class Token(BaseModel):
    """Token model"""
    access_token : str
    token_type : str

class Users(Base):
    """DB model for user details"""
    __tablename__= 'Users'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    email = Column(String,nullable=False, unique=True)
    password = Column(String, nullable=False, unique = True)
    is_active = Column(Boolean, server_default=text('false'))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
