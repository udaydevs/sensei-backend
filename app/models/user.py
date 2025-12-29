"""User Model"""
from pydantic import BaseModel


class Login(BaseModel):
    """
    Model for authentication
    """
    username : str
    password : str
