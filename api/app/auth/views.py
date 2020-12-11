from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging
import os

from ..database import get_db
from ..config import settings
from . import schemas, models, crud
from .security import authenticate_user, confirm_password_reset, create_access_token, get_current_active_user, verify_password
from .security import get_email_confirmation_link, password_reset_token, get_user_by_username, confirm_email_address
from .security import hash_password
from ..util.mail import send_mail
from ..util.exceptions import UniquValueException

logger = logging.getLogger('app')

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


@router.get('/users/me', response_model=schemas.UserDetail)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user


@router.patch('/users/me', response_model=schemas.UserDetail)
def update_user_me(
            update_user: schemas.UserUpdate,
            current_user: models.User = Depends(get_current_active_user),
            db: Session = Depends(get_db)
        ):
    user = crud.update_user(db, update_user, current_user.id)
    return user


@router.post('/users/me/update_password')
def update_password_me(
            password_update: schemas.PasswordUpdate,
            current_user: models.User = Depends(get_current_active_user),
            db: Session = Depends(get_db)
        ):
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password',
        )
    else:
        current_user.hashed_password = hash_password(password_update.password)
        db.commit()
        return {'detail': 'ok'}


@router.post('/register', response_model=schemas.UserDetail, status_code=status.HTTP_201_CREATED)
def register(user_create: schemas.UserCreate, tasks: BackgroundTasks, db: Session = Depends(get_db)):
    logger.info('Got request to register new user.')

    try:
        user = crud.create_user(db, user_create)
    except UniquValueException as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'Error: {exc}'
        )

    confirm_link = get_email_confirmation_link(router.url_path_for('confirm_email'), user.email)

    with open(os.path.join(os.path.dirname(__file__), 'templates/verifyemail.txt')) as f:
        body = f.read().format(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            verify_link=confirm_link
        )

    tasks.add_task(
        send_mail,
        subject='Verify your email for Fast Astro.',
        body=body,
        to=user.email
    )
    return user


@router.get('/confirm_email')
def confirm_email(token: str, db: Session = Depends(get_db)):
    user = confirm_email_address(db, token)
    if user.email_verified:
        return {'detail': 'ok'}
    else:
        return {'error': 'Address not verified'}


@router.post('/reset_password')
def request_password_reset(reset: schemas.PasswordResetRequest, tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = get_user_by_username(db, reset.email)
    if not user or not user.email_verified:
        return {'detail': 'ok'}

    reset_token = password_reset_token(user.email)
    reset_link = 'https://todo.local?token=' + reset_token
    with open(os.path.join(os.path.dirname(__file__), 'templates/resetpassword.txt')) as f:
        body = f.read().format(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            reset_link=reset_link
        )
    tasks.add_task(
        send_mail,
        subject='Fast Astro password reset.',
        body=body,
        to=user.email
    )

    return {'detail': 'ok'}


@router.post('/password_reset_confirm')
def password_reset_confirm(reset: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    confirm_password_reset(db, reset.token, reset.password)
    return {'detail': 'ok'}
