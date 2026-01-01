"""Authentication securities are defined here"""
from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from jose import jwt, JWTError
from app.core.config import settings
from app.models.user import Login

ALGORITHM = 'HS256'
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_jwt_token(data: dict):
    """
    Generate a jwt token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp" : expire})
    return jwt.encode( to_encode, settings.SECRET_KEY ,algorithm=ALGORITHM)

def verify_jwt_token(token: str):
    """
    To verify the jwt token
    """
    try:
        decode_token  = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.utcfromtimestamp(decode_token.get('exp'))>=datetime.utcnow():
            return decode_token
    except JWTError as e:
        return e

async def get_current_user(credentials : Annotated[str, Depends(oauth2_bearer)]):
    """
    To get the current user on every request
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        email : str = payload.get('email')
        user_id : int = payload.get('id')
        name : str = payload.get('name')
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )
        return {"name": name, "user_id": user_id, "email" : email}
    except JWTError:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "Could not validate user"
        )
