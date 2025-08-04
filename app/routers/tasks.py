from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.models import Task, User
from .helpers import get_db, get_current_user

router = APIRouter()


@router.post("/", response_model=TaskOut)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    new = Task(**task.dict(), owner_id=user.id)
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new


@router.get("/", response_model=List[TaskOut])
async def read_tasks(status: Optional[bool] = None, sort: Optional[str] = None, db: AsyncSession = Depends(get_db),
                     user: User = Depends(get_current_user)):
    q = select(Task).where(Task.owner_id == user.id)
    if status is not None:
        q = q.filter(Task.is_completed == status)
    if sort == "priority":
        q = q.order_by(Task.priority)
    elif sort == "-priority":
        q = q.order_by(-Task.priority)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskOut)
async def read_task(task_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You can't access this task")
    return task


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db),
                      user: User = Depends(get_current_user)):
    db_task = await db.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You can't update this task")

    for k, v in task.dict().items():
        setattr(db_task, k, v)
    await db.commit()
    await db.refresh(db_task)
    return db_task


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(get_current_user)):
    db_task = await db.get(Task, task_id)

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You can't delete this task")

    await db.delete(db_task)
    await db.commit()
    return {"status": "success"}
