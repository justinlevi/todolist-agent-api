import strawberry
from strawberry.types import Info
from typing import List, Optional
from datetime import datetime
from prisma import Prisma
from src.models.todo import TodoCreate


@strawberry.type
class Todo:
    id: int
    title: str
    completed: bool
    created_at: datetime
    due_date: Optional[datetime]
    weight: int
    parent_id: Optional[int]
    children: List[int]
    tags: List[str]


@strawberry.type
class Query:
    @strawberry.field
    async def hello(self) -> str:
        return "Hello World"

    @strawberry.field
    async def todos(self) -> List[Todo]:
        async with Prisma() as db:
            todos = await db.todo.find_many(include={"children": True})
            return [
                Todo(
                    id=todo.id,
                    title=todo.title,
                    completed=todo.completed,
                    created_at=todo.createdAt,
                    due_date=todo.dueDate,
                    weight=todo.weight,
                    parent_id=todo.parentId,
                    children=[child.id for child in todo.children],
                    tags=todo.tags.split(",") if todo.tags else [],
                )
                for todo in todos
            ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_todo(
        self,
        title: str,
        due_date: Optional[datetime] = None,
        weight: int = 1,
        parent_id: Optional[int] = None,
        tags: List[str] = [],
    ) -> Todo:
        try:
            todo_data = TodoCreate(
                title=title,
                dueDate=due_date,
                weight=weight,
                parentId=parent_id,
                tags=tags,
            )
            async with Prisma() as db:
                todo = await db.todo.create(
                    data={
                        "title": todo_data.title,
                        "dueDate": todo_data.dueDate,
                        "weight": todo_data.weight,
                        "parentId": todo_data.parentId,
                        "tags": ",".join(todo_data.tags),
                    }
                )
                return Todo(
                    id=todo.id,
                    title=todo.title,
                    completed=todo.completed,
                    created_at=todo.createdAt,
                    due_date=todo.dueDate,
                    weight=todo.weight,
                    parent_id=todo.parentId,
                    children=[],
                    tags=todo_data.tags,
                )
        except Exception as e:
            raise Exception(f"Failed to create todo: {str(e)}")

    @strawberry.mutation
    async def toggle_todo(self, id: int) -> Todo:
        try:
            async with Prisma() as db:
                todo = await db.todo.find_unique(
                    where={"id": id}, include={"children": True}
                )
                if todo is None:
                    raise Exception(f"Todo with id {id} not found")
                updated_todo = await db.todo.update(
                    where={"id": id},
                    data={"completed": not todo.completed},
                    include={"children": True},
                )
                if updated_todo is None:
                    raise Exception(f"Failed to update todo with id {id}")
                return Todo(
                    id=updated_todo.id,
                    title=updated_todo.title,
                    completed=updated_todo.completed,
                    created_at=updated_todo.createdAt,
                    due_date=updated_todo.dueDate,
                    weight=updated_todo.weight,
                    parent_id=updated_todo.parentId,
                    children=[child.id for child in updated_todo.children],
                    tags=updated_todo.tags.split(",") if updated_todo.tags else [],
                )
        except Exception as e:
            raise Exception(f"Failed to toggle todo: {str(e)}")

    @strawberry.mutation
    async def delete_todo(self, id: int) -> bool:
        try:
            async with Prisma() as db:
                todo = await db.todo.find_unique(where={"id": id})
                if todo is None:
                    raise Exception(f"Todo with id {id} not found")

                deleted_todo = await db.todo.delete(where={"id": id})
                if deleted_todo is None:
                    raise Exception(f"Failed to delete todo with id {id}")

                return True
        except Exception as e:
            raise Exception(f"Failed to delete todo: {str(e)}")


schema = strawberry.Schema(query=Query, mutation=Mutation)
