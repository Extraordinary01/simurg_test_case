import jwt
import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
SECRET_KEY = os.getenv("SECRET_KEY", "secret")


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload.get("sub")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user
