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


class UserCreate(BaseUser):
    password: constr(min_length=8)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    password: str
