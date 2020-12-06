from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class TokenData(BaseModel):
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str


class BaseUser(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserDetail(BaseUser):
    id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(BaseUser):
    password: constr(min_length=8)
