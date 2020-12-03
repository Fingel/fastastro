from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from . import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/sources",
    tags=["sources"]
)


@router.get('/', response_model=List[schemas.ListSource])
def get_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sources(db, skip=skip, limit=limit)


@router.post('/', response_model=schemas.Source)
def create_source(source: schemas.CreateSource, db: Session = Depends(get_db)):
    return crud.create_source(db, source)


@router.get('/{source_id}', response_model=schemas.Source)
def get_source(source_id: int, db: Session = Depends(get_db)):
    return crud.get_source(db, source_id)


@router.post('/{source_id}/comment', response_model=schemas.Comment)
def create_comment(source_id: int, comment: schemas.Comment, db: Session = Depends(get_db)):
    return crud.create_comment(db, comment, source_id)
