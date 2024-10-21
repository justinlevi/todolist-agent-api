import strawberry
from strawberry.types import Info
from typing import List
from datetime import datetime
from prisma import Prisma


@strawberry.type
class Todo:
    id: int
    title: str
    completed: bool
    created_at: datetime


@strawberry.type
class Query:
    @strawberry.field
    async def hello(self) -> str:
        return "Hello World"

    @strawberry.field
    async def todos(self) -> List[Todo]:
        async with Prisma() as db:
            todos = await db.todo.find_many()
            return [
                Todo(
                    id=todo.id,
                    title=todo.title,
                    completed=todo.completed,
                    created_at=todo.createdAt,
                )
                for todo in todos
            ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_todo(self, title: str) -> Todo:
        try:
            async with Prisma() as db:
                todo = await db.todo.create(data={"title": title})
                return Todo(
                    id=todo.id,
                    title=todo.title,
                    completed=todo.completed,
                    created_at=todo.createdAt,
                )
        except Exception as e:
            raise Exception(f"Failed to create todo: {str(e)}")

    @strawberry.mutation
    async def toggle_todo(self, id: int, info: Info) -> Todo:
        try:
            async with Prisma() as db:
                todo = await db.todo.find_unique(where={"id": id})
                if todo is None:
                    raise Exception(f"Todo with id {id} not found")
                updated_todo = await db.todo.update(
                    where={"id": id}, data={"completed": not todo.completed}
                )
                if updated_todo is None:
                    raise Exception(f"Failed to update todo with id {id}")
                return Todo(
                    id=updated_todo.id,
                    title=updated_todo.title,
                    completed=updated_todo.completed,
                    created_at=updated_todo.createdAt,
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
