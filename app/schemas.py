from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    priority: Optional[int] = 0


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskOut(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
