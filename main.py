from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from auth import authenticate_user, create_access_token, get_current_active_user, Token, User, get_db, get_password_hash
from datetime import timedelta
from Books import router as books_router, books
from Models import UserCreate

app = FastAPI ()

app.mount ("/static", StaticFiles (directory="static"), name="static")
templates = Jinja2Templates (directory="templates")

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post ("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends (), db: Session = Depends (get_db)):
    user = authenticate_user (db, form_data.username, form_data.password)
    if not user:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta (minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token (
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post ("/register", response_model=UserCreate)
async def register_user(user: UserCreate, db: Session = Depends (get_db)):
    db_user = get_user (db, username=user.username)
    if db_user:
        raise HTTPException (status_code=400, detail="Username already registered")
    hashed_password = get_password_hash (user.password)
    db_user = User (
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=False
    )
    db.add (db_user)
    db.commit ()
    db.refresh (db_user)
    return db_user


@app.get ("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse ("home.html", {"request": request, "books": books})


@app.get ("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse ("login.html", {"request": request})


@app.get ("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse ("register.html", {"request": request})


app.include_router (books_router, prefix="/api")
