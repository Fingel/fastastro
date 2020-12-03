from typing import List
from sqlalchemy.orm import Session

from . import models, schemas


def get_source(db: Session, source_id: int) -> models.Source:
    return db.query(models.Source).filter(models.Source.id == source_id).first()


def get_sources(db: Session, skip: int = 0, limit: int = 0) -> List[models.Source]:
    return db.query(models.Source).offset(skip).limit(limit).all()


def create_source(db: Session, source: schemas.CreateSource) -> models.Source:
    db_source = models.Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def create_comment(db: Session, comment: schemas.Comment, source_id: int) -> models.Comment:
    db_comment = models.Comment(**comment.dict(), source_id=source_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
