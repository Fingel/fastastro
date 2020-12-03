from fastapi import Query
from dataclasses import dataclass
from pydantic import BaseModel
import math

EARTH_RADIUS_METERS = 6371008.77141506


class ListQueryParams(BaseModel):
    """
    Query parameters common to list operations
    """
    skip: int = Query(0)
    limit: int = Query(100, ge=1)
    order_by: str = Query(None)


def degrees_to_meters(degrees: float) -> float:
    """
    Convert degrees to meters for use with PostGIS geography functions
    """
    return 2 * math.pi * EARTH_RADIUS_METERS * degrees / 360


def wkt_point(ra: float, dec: float, srid: int) -> str:
    """
    Returns a Point a Well Known Text format given RA/Dec and SRID
    """
    return f'srid={srid};POINT({ra} {dec})'
