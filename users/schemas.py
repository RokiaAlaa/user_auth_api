from ninja import Schema
from pydantic import EmailStr
from typing import Optional

class RegisterSchema(Schema):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class LoginSchema(Schema):
    username: str
    password: str

class UserOutSchema(Schema):
    id: int
    username: str
    email: str
    first_name: Optional[str] = None

class TokenSchema(Schema):
    access_token: str
    refresh_token: str

class RefreshSchema(Schema):
    refresh_token: str

class UserUpdateSchema(Schema):
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None