from calendar import month

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Database configuration
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine (DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker (autocommit=False, autoflush=False, bind=engine)
Base = declarative_base ()

# Secret key to encode JWT tokens
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext (schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer (tokenUrl="token")


# User model
class User (Base):
    __tablename__ = "users"
    username = Column (String, primary_key=True, index=True)
    email = Column (String, unique=True, index=True, nullable=True)
    full_name = Column (String, nullable=True)
    hashed_password = Column (String)
    disabled = Column (Boolean, default=False)


# Create the database tables
Base.metadata.create_all (bind=engine)


# Pydantic models
class UserInDB (BaseModel):
    username: str
    email: Optional [str] = None
    full_name: Optional [str] = None
    disabled: Optional [bool] = None
    hashed_password: str


class Token (BaseModel):
    access_token: str
    token_type: str


class TokenData (BaseModel):
    username: Optional [str] = None


# Dependency to get the database session
def get_db():
    db = SessionLocal ()
    try:
        yield db
    finally:
        db.close ()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify (plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash (password)


def get_user(db: Session, username: str):
    return db.query (User).filter (User.username == username).first ()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user (db, username)
    if not user:
        return False
    if not verify_password (password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional [timedelta] = None):
    to_encode = data.copy ()
    if expires_delta:
        expire = datetime.now () + expires_delta
    else:
        expire = datetime.now () + timedelta (minutes=15)
    to_encode.update ({"exp": expire})
    encoded_jwt = jwt.encode (to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends (oauth2_scheme), db: Session = Depends (get_db)):
    credentials_exception = HTTPException (
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode (token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get ("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData (username=username)
    except JWTError:
        raise credentials_exception
    user = get_user (db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends (get_current_user)):
    if current_user.disabled:
        raise HTTPException (status_code=400, detail="Inactive user")
    return current_user
