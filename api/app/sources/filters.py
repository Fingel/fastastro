from fastapi import Query
from pydantic import BaseModel


class SourceFilter(BaseModel):
    """
    Query params specific to listing Sources
    """
    name_contains: str = Query(None)
    cone_ra: float = Query(None, ge=-360, le=360)
    cone_dec: float = Query(None, ge=-90, le=90)
    cone_radius: float = Query(None)

    @property
    def cone(self) -> tuple:
        if all((self.cone_ra, self.cone_dec, self.cone_radius)):
            return (self.cone_ra, self.cone_dec, self.cone_radius)
        return ()
