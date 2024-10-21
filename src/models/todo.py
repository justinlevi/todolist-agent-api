from pydantic import BaseModel
from datetime import datetime


class TodoCreate(BaseModel):
    title: str


class Todo(BaseModel):
    id: int
    title: str
    completed: bool
    createdAt: datetime
