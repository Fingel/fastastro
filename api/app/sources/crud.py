from typing import List
from sqlalchemy.orm import Session

from . import models, schemas, filters
from ..util.web import ListQueryParams
from ..util.calc import degrees_to_meters, wkt_point
from ..config import settings


def get_source(db: Session, source_id: int) -> models.Source:
    return db.query(models.Source).filter(models.Source.id == source_id).first()


def get_sources(db: Session, list_params: ListQueryParams, source_filter: filters.SourceFilter) -> List[models.Source]:
    query = db.query(models.Source)

    if source_filter.name_contains:
        query = query.filter(models.Source.name.contains(source_filter.name_contains))

    if source_filter.cone:
        ra, dec, radius = source_filter.cone
        query = query.filter(
            models.Source.location.ST_DWithin(wkt_point(ra, dec, settings.srid), degrees_to_meters(radius))
        )

    return query.order_by(list_params.order_by).offset(list_params.skip).limit(list_params.limit).all()


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
