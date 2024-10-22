from prisma import Prisma
from src.services.todos.todos_service import TodosService
from strawberry.fastapi import BaseContext
from typing import Optional


class GraphQLContext(BaseContext):
    prisma: Prisma
    todos_service: TodosService

    def __init__(self):
        super().__init__()
        self.prisma = Prisma()
        self.todos_service = TodosService(self.prisma)

    async def __aenter__(self):
        await self.prisma.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.prisma.disconnect()


async def get_context() -> GraphQLContext:
    context = GraphQLContext()
    await context.__aenter__()
    return context
