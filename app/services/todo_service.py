from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.models import ToDo


# Create a ToDo
async def create_todo(db: AsyncSession, todo: schemas.ToDoCreate, owner_id: int):
    db_todo = ToDo(**todo.dict(), owner_id=owner_id)

    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)

    return db_todo

# get all the ToDos
async def get_todos(db: AsyncSession, limit: int, offset: int, completed: bool, owner_id: int):
    query = select(models.ToDo).where(ToDo.owner_id == owner_id)
    if completed is not None:
        query = query.filter(models.ToDo.completed == completed)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)

    return result.scalars().all()

async def get_todos_cursor(db: AsyncSession, limit: int, cursor: int | None, owner_id: int):
    query = select(models.ToDo).where(ToDo.owner_id == owner_id).order_by(models.ToDo.id)
    if cursor:
        query = query.where(models.ToDo.id > cursor)

    query = query.limit(limit)
    result = await db.execute(query)
    todos = result.scalars().all()

    next_cursor = None
    if todos:
        next_cursor = todos[-1].id

    return {
        "items": todos,
        "next_cursor": next_cursor,
    }

# get ToDo by Id
async def get_todo(db: AsyncSession, todo_id: int, owner_id: int):
    query = select(models.ToDo).where(models.ToDo.id == todo_id, ToDo.owner_id == owner_id)
    result = await db.execute(query)

    return result.scalar_one_or_none()

# update specified ToDo
async def update_todo(db: AsyncSession, todo_id: int, updated_todo: schemas.ToDoUpdate, owner_id: int):
    todo = await get_todo(db, todo_id, owner_id)
    if not todo:
        return None

    todo.title = updated_todo.title
    todo.description = updated_todo.description
    todo.completed = updated_todo.completed

    await db.commit()
    await db.refresh(todo)

    return todo

# patch specified ToDo
async def patch_todo(db: AsyncSession, todo_id: int, patch: schemas.ToDoPatch, owner_id: int):
    todo = await get_todo(db, todo_id, owner_id)
    if not todo:
        return None

    todo.completed = patch.completed

    await db.commit()
    await db.refresh(todo)

    return todo

# delete the specified ToDo
async def delete_todo(db: AsyncSession, todo_id: int, owner_id: int):
    todo = await get_todo(db, todo_id, owner_id)
    if not todo:
        return None

    await db.delete(todo)
    await db.commit()

    return todo

