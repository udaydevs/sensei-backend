"""User Model"""
from pydantic import BaseModel
from pydantic import EmailStr


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
