"""Authentication securities are defined here"""
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from app.core.config import Settings

security = HTTPBearer()
ALGORITHM = 'HS256'

def create_jwt_token(data: dict):
    """Create jwt token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expire" : expire})
    encoded_jwt = jwt.encode( to_encode, Settings.SECRET_KEY ,algorithm=ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str):
    """
    To verify the jwt token
    """
    try:
        decode_token  = jwt.decode(token, Settings.SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.utcfromtimestamp(decode_token.get('exp'))>=datetime.utcnow():
            return decode_token
    except JWTError as e:
        return e

async def get_current_user(credentials : HTTPAuthorizationCredentials = Security(security)):
    """
    To get the current user on every request
    """
    token = credentials.credentials
    payloads = verify_jwt_token(token=token)
    print(payloads)
    if payloads is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payloads
