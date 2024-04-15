""" This module contains the endpoints for the authentication of the API. """
from datetime import datetime, timedelta, timezone
from typing import Annotated
from app.models import  database, user
from app.models.user import  UsersCreate,User
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import  OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

router = APIRouter(
    prefix="/api/auth",
)

SECRET_KEY = "9296409bf57ded5efe4e4499b07dc6251ce35c3617e366f0e3ffe96af641383bb1f85bca4107dc74feae9a5fd9d6554e01e6114e22900cae5d9594d1d7295aa2c69bc492b48a723e25ffb0dfab86b045"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oatuh2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

DbDependency = Annotated[Session, Depends(database.get_db)]


@router.post("/signup",  status_code=status.HTTP_201_CREATED, tags=["auth"])
def auth_signup(db: DbDependency, user_request: UsersCreate):
    """ Allows you to create an account with fields for username, email, and password. 
    The name and email must be unique on the platform, 
    while the password must follow minimum security guidelines. Additionally, 
    the password must be entered twice for the user to confirm that it is entered correctly. """
    password1 = user_request.password1
    password2 = user_request.password2
    username = user_request.username
    email = user_request.email
    if password1 != password2:
        return {"message": "Passwords do not match"}

    db_user = db.query(User).filter(User.username == username).one_or_none()
    if db_user is not None:
        return {"message": "Username already exists"}

    db_user = db.query(User).filter(User.email == email).one_or_none()
    if db_user is not None:
        return {"message": "Email already exists"}

    new_user = User(username=username, email=email, password1=password1, password2=password2)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@router.post("/login",  tags=["auth"])
def auth_login(user_request: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDependency):
    """ Allows you to retrieve the authorization token to consume the API resources by 
    providing the username and password of a previously registered account. """
    username = user_request.username
    password = user_request.password
    db_user = db.query(User).filter(User.username == username,
                                         User.password1 == password).one_or_none()

    if db_user is None:
        return {
            "message": "Username or password are not correct"
        }
    token = _create_access_token(db_user.username, db_user.id,timedelta(minutes=20))
    return {
        "access_token": token,
        "token_type": "bearer",
        "email": db_user.email,
        "id": db_user.id
    }


def _create_access_token(username: str, user_id: int, expires_delta: timedelta):
    """ This function is used to create the access token."""
    encode = { 'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({ 'exp': expires })
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oatuh2_bearer)]):
    """ This function is used to get the current user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
                            ,detail='Invalid token, or something went wrong. ') from exc
