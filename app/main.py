from fastapi import FastAPI

from .models import Base, User, ToDo
from app.database import engine
from app.routers import todos, auth

app = FastAPI()
app.include_router(todos.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

