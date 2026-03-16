from pydantic import BaseModel
from typing import Union

# User Schemas
class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    model_config = {
        "from_attributes": True
    }

# ToDo Schemas
class ToDoCreate(BaseModel):
    title: str
    description: Union[str, None] = None

class ToDo(BaseModel):
    id: int
    title: str
    description: Union[str, None] = None
    completed: bool = False
    owner_id: int
    model_config = {
        "from_attributes": True
    }

class ToDoUpdate(BaseModel):
    title: str
    description: Union[str, None] = None
    completed: bool

class ToDoPatch(BaseModel):
    completed: bool