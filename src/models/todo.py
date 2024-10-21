from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class TodoCreate(BaseModel):
    title: str
    dueDate: Optional[datetime] = None
    weight: int = 1
    parentId: Optional[int] = None
    tags: List[str] = []


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
