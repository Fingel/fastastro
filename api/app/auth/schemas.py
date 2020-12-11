from typing import Optional
from pydantic import BaseModel, EmailStr, constr


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
    is_active: bool
    is_superuser: bool
    email_verified: bool


class PasswordMixin(BaseModel):
    password: constr(min_length=8)


class UserCreate(PasswordMixin, BaseUser):
    pass


class UserUpdate(BaseUser):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    password: str


class PasswordUpdate(PasswordMixin, BaseModel):
    current_password: str
