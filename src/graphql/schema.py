import strawberry
from strawberry.types import Info
from typing import List, Optional
from datetime import datetime
from prisma import Prisma
from src.models.todo import TodoCreate, TodoUpdate, Todo as TodoModel
from src.services.todos.todos_service import TodosService
from src.graphql.context import GraphQLContext


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

    @classmethod
    def from_pydantic(cls, todo: TodoModel):
        return cls(
            id=todo.id,
            title=todo.title,
            completed=todo.completed,
            created_at=todo.createdAt,
            due_date=todo.dueDate,
            weight=todo.weight,
            parent_id=todo.parentId,
            children=todo.children,
            tags=todo.tags,
        )


@strawberry.input
class CreateTodoInput:
    title: str
    completed: bool = False
    due_date: Optional[datetime] = None
    weight: int = 1
    parent_id: Optional[int] = None
    children: List[int] = strawberry.field(default_factory=list)
    tags: List[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateTodoInput:
    id: int
    title: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    weight: Optional[int] = None
    parent_id: Optional[int] = None
    children: Optional[List[int]] = None
    tags: Optional[List[str]] = None


@strawberry.type
class Query:
    @strawberry.field
    async def hello(self) -> str:
        return "Hello World"

    @strawberry.field
    async def todos(self, info: Info[GraphQLContext, None]) -> List[Todo]:
        try:
            todos = await info.context.todos_service.get_todos()
            return [Todo.from_pydantic(todo) for todo in todos]
        except Exception as e:
            raise Exception(f"Failed to fetch todos: {str(e)}")


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_todo(
        self, info: Info[GraphQLContext, None], data: CreateTodoInput
    ) -> Todo:
        try:
            todo_data = TodoCreate(
                title=data.title,
                completed=data.completed,
                dueDate=data.due_date,
                weight=data.weight,
                parentId=data.parent_id,
                children=data.children,
                tags=data.tags,
            )
            created_todo = await info.context.todos_service.create_todo(todo_data)
            return Todo.from_pydantic(created_todo)
        except Exception as e:
            raise Exception(f"Failed to create todo: {str(e)}")

    @strawberry.mutation
    async def toggle_todo(self, info: Info[GraphQLContext, None], id: int) -> Todo:
        try:
            toggled_todo = await info.context.todos_service.toggle_todo(id)
            return Todo.from_pydantic(toggled_todo)
        except Exception as e:
            raise Exception(f"Failed to toggle todo: {str(e)}")

    @strawberry.mutation
    async def update_todo(
        self, info: Info[GraphQLContext, None], data: UpdateTodoInput
    ) -> Todo:
        try:
            todo_data = TodoUpdate(
                title=data.title,
                completed=data.completed,
                dueDate=data.due_date,
                weight=data.weight,
                parentId=data.parent_id,
                children=data.children,
                tags=data.tags,
            )
            updated_todo = await info.context.todos_service.update_todo(
                data.id, todo_data
            )
            return Todo.from_pydantic(updated_todo)
        except Exception as e:
            raise Exception(f"Failed to update todo: {str(e)}")

    @strawberry.mutation
    async def delete_todo(self, info: Info[GraphQLContext, None], id: int) -> bool:
        try:
            await info.context.todos_service.delete_todo(id)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete todo: {str(e)}")


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        # Add an extension to inject the TodosService into the context
        # This will depend on how you're setting up your GraphQL server
    ],
)
