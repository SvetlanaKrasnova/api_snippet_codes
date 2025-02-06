from calendar import timegm
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class CurrentUserSchema(BaseModel):
    sub: Optional[str]
    role: Optional[str]
    exp: Optional[timegm] = None

    def __bool__(self):
        return False if not self.sub and not self.role else True
