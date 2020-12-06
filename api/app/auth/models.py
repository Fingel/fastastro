from sqlalchemy import Column, String, Boolean

from ..database import Base


class User(Base):
    email = Column(String(length=255), unique=True, index=True, nullable=False)
    first_name = Column(String(length=255), nullable=False)
    last_name = Column(String(length=255), nullable=False)
    hashed_password = Column(String(length=2000), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
