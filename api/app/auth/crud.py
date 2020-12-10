from sqlalchemy.orm import Session
from sqlalchemy import exists

from . import models, schemas
from .security import hash_password
from ..util.exceptions import UniquValueException


def create_user(db: Session, create_user: schemas.UserCreate) -> models.User:
    if db.query(exists().where(models.User.email == create_user.email)).scalar():
        raise UniquValueException(
            'User with this email already exists.',
            field='email',
            value=create_user.email
        )

    hashed_password = hash_password(create_user.password)
    db_user = models.User(hashed_password=hashed_password, **create_user.dict(exclude={'password'}))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
