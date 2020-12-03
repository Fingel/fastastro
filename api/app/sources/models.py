from sqlalchemy import Column, String, JSON, Integer
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography, shape
from sqlalchemy.sql.schema import ForeignKey

from ..database import Base
from ..config import settings


class Source(Base):
    name = Column(String, index=True)
    location = Column(Geography('POINT', srid=settings.srid), nullable=False, index=True)
    data = Column(JSON)

    comments = relationship('Comment', back_populates='source')

    def __init__(self, *args, **kwargs):
        """
        Convert the ra/dec fields from the schema into the PostGIS text representation
        """
        ra = kwargs.pop('ra')
        dec = kwargs.pop('dec')
        kwargs['location'] = f'srid={settings.srid};POINT({ra} {dec})'

        return super().__init__(*args, **kwargs)

    @property
    def ra(self):
        ra = shape.to_shape(self.location).x
        if ra < 0:
            ra = ra + 360
        return ra

    @property
    def dec(self):
        return shape.to_shape(self.location).y


class Comment(Base):
    content = Column(String)
    source_id = Column(Integer, ForeignKey('source.id'))

    source = relationship('Source', back_populates='comments')
