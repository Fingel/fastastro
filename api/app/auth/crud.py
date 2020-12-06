from sqlalchemy.orm import Session

from . import models, schemas
from .security import hash_password


def create_user(db: Session, create_user: schemas.UserCreate) -> models.User:
    hashed_password = hash_password(create_user.password)
    db_user = models.User(hashed_password=hashed_password, **create_user.dict(exclude={'password'}))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
