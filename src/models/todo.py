from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class TodoCreate(BaseModel):
    title: str
    completed: bool = False
    dueDate: Optional[datetime] = None
    weight: int = 1
    parentId: Optional[int] = None
    children: List[int] = []
    tags: List[str] = []


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    dueDate: Optional[datetime] = None
    weight: Optional[int] = None
    parentId: Optional[int] = None
    children: Optional[List[int]] = None
    tags: Optional[List[str]] = None


class Todo(BaseModel):
    id: int
    title: str
    completed: bool
    createdAt: datetime
    dueDate: Optional[datetime] = None
    weight: int
    parentId: Optional[int] = None
    children: List[int] = []
    tags: List[str] = []

    class Config:
        from_attributes = True
