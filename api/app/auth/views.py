from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..config import settings
from . import schemas, models, crud
from .security import authenticate_user, create_access_token, get_current_active_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post('/token', response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token_expires = timedelta(settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={'sub': user.email}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.get("/users/me/", response_model=schemas.UserDetail)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user


@router.post('/register', response_model=schemas.UserDetail)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user_create)
