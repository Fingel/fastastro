from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from ..database import get_db
from ..config import settings
from . import schemas, models

JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_user_by_username(db: Session, username: str) -> models.User:
    return db.query(models.User).filter_by(email=username).first()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(settings.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, JWT_ALGORITHM)

    return encoded_jwt


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate':  'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
        username: str = payload.get('sub', '')
        if not username:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


def get_email_confirmation_link(route: str, email: str) -> str:
    confirm_token = create_access_token({'sub': email}, expires_delta=timedelta(hours=2))
    return'{route}?token={token}'.format(
        route=route,
        token=confirm_token
    )


def confirm_email_address(db: Session, token: str) -> models.User:
    token_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Could not validate email, please try again by requesting the email be re-sent.'
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise token_exception
    email: str = payload.get('sub', '')
    if not email:
        raise token_exception

    user = get_user_by_username(db, username=email)
    if not user:
        raise token_exception

    user.email_verified = True
    db.commit()
    db.refresh(user)

    return user


def password_reset_token(email: str) -> str:
    return create_access_token({'sub': email}, expires_delta=timedelta(hours=2))


def confirm_password_reset(db: Session, token: str, password: str) -> models.User:
    token_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Could not validate request, please try again by resetting your password again.'
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise token_exception
    email: str = payload.get('sub', '')
    if not email:
        raise token_exception

    user = get_user_by_username(db, username=email)
    if not user or not user.email_verified:
        raise token_exception

    user.hashed_password = hash_password(password)
    db.commit()
    db.refresh(user)

    return user
