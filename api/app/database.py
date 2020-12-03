from datetime import date
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from datetime import datetime

from .config import settings

SQLALCHEMY_DATABASE_URL = settings.db_string

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class BaseModel:
    """
    The BaseModel contains columns and configuration that will apply to all
    models
    """
    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=BaseModel)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
