"""The page for the authentication purpose"""
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Security,status, Depends

security = HTTPBearer()
SECRET_KEY = "alskdjfieansviewh23iu509r4hgvn3g948hbn3984hbnv349"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
fake_user_db = {
    'udaysingh' : {'username' : 'udaysingh', 'password' : '#1Engineer'}
}


class Login(BaseModel):
    """
    Model for authentication
    """
    username : str
    password : str


# @app.post('/login/')
async def login_user(user:Login):
    """
    Generation of the token
    """
    db_user = fake_user_db.get(user.username)
    if not db_user or db_user["password"] != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token_data = {'sub' : user.username}
    token = create_jwt_token(data=token_data)
    return { 'token' : token, 'token_type' : 'Bearer'}

def create_jwt_token(data: dict):
    """
    The function to create a jwt token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp' : expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

def verify_jwt_token(token: str):
    """
    To verify the jwt token
    """
    try:
        decode_token  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.utcfromtimestamp(decode_token.get('exp'))>=datetime.utcnow():
            return decode_token
    except jwt.PyJWTError:
        return None


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

# @app.get('/protected')
async def protected_route(current_user : dict = Depends(get_current_user)):
    """
    Test route
    """
    return {'msg' : f'Hello, {current_user['sub']}!, You are authenticated.'}
