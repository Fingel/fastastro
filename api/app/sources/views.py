from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from . import crud, schemas, filters
from ..database import get_db
from ..util.web import ListQueryParams

router = APIRouter(
    prefix="/sources",
    tags=["sources"]
)


@router.get('/', response_model=List[schemas.ListSource])
def get_sources(
        list_params: ListQueryParams = Depends(),
        source_filter: filters.SourceFilter = Depends(),
        db: Session = Depends(get_db)
        ):
    return crud.get_sources(db, list_params, source_filter)


@router.post('/', response_model=schemas.Source)
def create_source(source: schemas.CreateSource, db: Session = Depends(get_db)):
    return crud.create_source(db, source)


@router.get('/{source_id}', response_model=schemas.Source)
def get_source(source_id: int, db: Session = Depends(get_db)):
    return crud.get_source(db, source_id)


@router.post('/{source_id}/comment', response_model=schemas.Comment)
def create_comment(source_id: int, comment: schemas.Comment, db: Session = Depends(get_db)):
    return crud.create_comment(db, comment, source_id)
