"""The apis for the authentication purpose"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.security import create_jwt_token, get_current_user
from app.models.user import Login
fake_user_db = {
    'udaysingh' : {'username' : 'udaysingh', 'password' : '#1Engineer'}
}

router = APIRouter(prefix='/auth')

@router.post('/login')
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

@router.get('/protected')
async def protected_route(current_user : dict = Depends(get_current_user)):
    """
    Test route
    """
    return {'msg' : f'Hello, {current_user['sub']}!, You are authenticated.'}
