from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas import UserCreate, UserOut
from app.models import User
from passlib.context import CryptContext
import jwt
import os
from fastapi.security import OAuth2PasswordRequestForm
from .helpers import get_db, get_current_user


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "secret")


def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    print(user)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def read_users_me(user: User = Depends(get_current_user)):
    return user
