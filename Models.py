from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate (BaseModel):
    username: str
    email: Optional [str] = None
    full_name: Optional [str] = None
    password: str


class User (UserCreate):
    disabled: Optional [bool] = None


class UserInDB (User):
    hashed_password: str


class Token (BaseModel):
    access_token: str
    token_type: str


class TokenData (BaseModel):
    username: Optional [str] = None


class UserUpdate (BaseModel):
    email: Optional [str] = None
    full_name: Optional [str] = None
    password: Optional [str] = None
    disabled: Optional [bool] = None


class UserInResponse (BaseModel):
    username: str
    email: Optional [str] = None
    full_name: Optional [str] = None
    disabled: Optional [bool] = None
    created_at: datetime
    updated_at: datetime
