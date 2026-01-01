"""The apis for the authentication purpose"""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import  OAuth2PasswordRequestForm
from passlib.context import CryptContext
from starlette import status
from app.core.database import DbDependency
from app.core.security import create_jwt_token, get_current_user
from app.models.user import Users, Register

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = 'auto')
router = APIRouter(prefix='/auth')

@router.post('/register')
async def create_user(user: Register, db:DbDependency):
    """
    Creates a new user using registration details(name, email and password)
    """
    get_user = db.query(Users).filter(Users.email == user.email).first()
    if get_user:
        return {"msg" : "User already exists", "status_code" : status.HTTP_400_BAD_REQUEST}
    user_model = Users(
        name = user.name,
        password = bcrypt_context.hash(user.password),
        email = user.email
    )
    db.add(user_model)
    db.commit()
    return {"msg" : "User Created Successfully", "status_code" : status.HTTP_201_CREATED}

def authenticate_user(email: str, password: str, db):
    """Verifies the username nad password """
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, str(user.password)):
        return False
    return user

@router.post('/login')
async def login_user(user:Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDependency):
    """
    Generation of the token and authentication takes place
    """
    email = user.username
    current_user = authenticate_user(email, user.password, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token_data = {'name' : current_user.name, 'email' : current_user.email}
    token = create_jwt_token(data=token_data)
    return { 'token' : token, 'token_type' : 'bearer'}

@router.get('/protected')
async def protected_route(current_user : dict = Depends(get_current_user)):
    """
    Test route
    """
    return {'msg' : f'Hello, {current_user['sub']}!, You are authenticated.'}
