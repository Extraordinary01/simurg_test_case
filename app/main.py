from fastapi import FastAPI
from app.database import init_db
from app.routers import auth, tasks

app = FastAPI(title="Task Management API")

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
