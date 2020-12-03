from typing import List, Any
from pydantic import BaseModel


class Comment(BaseModel):
    content: str

    class Config:
        orm_mode = True


class BaseSource(BaseModel):
    name: str
    ra: float
    dec: float
    data: Any = None

    class Config:
        orm_mode = True


class CreateSource(BaseSource):
    """
    Fields which should be required for creating a source
    """
    pass


class Source(BaseSource):
    """
    Fields for displaying a single Source
    """
    id: int
    comments: List[Comment] = []


class ListSource(BaseSource):
    """
    Fields which should be displayed when listing sources
    """
    id: int
