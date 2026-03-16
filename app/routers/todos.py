import os
from typing import Union

from jose import jwt
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ..services import todo_service
from .. import schemas
from ..database import AsyncSessionLocal

router = APIRouter(
    prefix="/todos",
    tags=["Todos"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SECRET_KEY = "supersecretkey"

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
        return int(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.ToDo)
async def create_todo(
        todo: schemas.ToDoCreate,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user)):
    return await todo_service.create_todo(db, todo, owner_id=user_id)

@router.get("/", response_model=list[schemas.ToDo])
async def get_todos(
        limit: int = 10,
        offset: int = 0,
        completed: Union[bool, None] = None,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user)):

    return await todo_service.get_todos(db, limit, offset, completed, owner_id=user_id)

@router.get("/cursor")
async def get_todos_cursor(
        limit: int = 5,
        cursor: Union[int, None] = None,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user)):
    return await todo_service.get_todos_cursor(db, limit, cursor, owner_id=user_id)

@router.get("/{todo_id}", response_model=schemas.ToDo)
async def get_todo(todo_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user)):
    todo = await todo_service.get_todo(db, todo_id, owner_id=user_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=schemas.ToDo)
async def update_todo(
        todo_id: int,
        updated_todo: schemas.ToDoUpdate,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user)):
    todo = await todo_service.update_todo(db, todo_id, updated_todo, owner_id=user_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    return todo

@router.patch("/{todo_id}", response_model=schemas.ToDo)
async def patch_todo(
        todo_id: int,
        updated_todo: schemas.ToDoPatch,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user)):
    todo = await todo_service.patch_todo(db, todo_id, updated_todo, owner_id=user_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    return todo

@router.delete("/{todo_id}")
async def delete_todo(
        todo_id: int,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user)):
    todo = await todo_service.delete_todo(db, todo_id, owner_id=user_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    return {"message": "Todo deleted"}