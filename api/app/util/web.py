from fastapi import Query
from pydantic import BaseModel


class ListQueryParams(BaseModel):
    """
    Query parameters common to list operations
    """
    skip: int = Query(0)
    limit: int = Query(100, ge=1)
    order_by: str = Query(None)
