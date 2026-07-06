from ninja import Schema
from pydantic import EmailStr
from typing import Optional

class RegisterSchema(Schema):
    username: str
    email: EmailStr
    password: str

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