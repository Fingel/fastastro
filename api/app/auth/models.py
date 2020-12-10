from sqlalchemy import Column, String, Boolean

from ..database import Base


class User(Base):
    email: str = Column(String(length=255), unique=True, index=True, nullable=False)
    first_name: str = Column(String(length=255), nullable=False)
    last_name: str = Column(String(length=255), nullable=False)
    hashed_password: str = Column(String(length=2000), nullable=False)
    email_verified: bool = Column(Boolean, default=False, nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
