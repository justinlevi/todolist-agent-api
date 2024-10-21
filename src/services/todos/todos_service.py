from typing import List, Optional
from datetime import datetime
from prisma import Prisma
from src.models.todo import Todo, TodoCreate


class TodosService:
    @staticmethod
    async def get_todos() -> List[Todo]:
        """
        Retrieve all todos from the database.

        This function fetches all todo items stored in the database and returns them as a list of Todo objects.

        Returns:
            List[Todo]: A list of Todo objects representing all the todos in the database.

        Raises:
            Exception: If there's an error while fetching the todos from the database.
        """
        try:
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
        except Exception as e:
            raise Exception(f"Failed to fetch todos: {str(e)}")

    @staticmethod
    async def create_todo(todo_data: TodoCreate) -> Todo:
        """
        Create a new todo item in the database.

        This function creates a new todo item with the given title and stores it in the database.

        Args:
            title (str): The title of the new todo item.

        Returns:
            Todo: A Todo object representing the newly created todo item.

        Raises:
            Exception: If there's an error while creating the todo in the database.
        """
        try:
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

    @staticmethod
    async def toggle_todo(id: int) -> Todo:
        """
        Toggle the completion status of a todo item.

        This function finds a todo item by its ID and toggles its completion status (completed or not completed).

        Args:
            id (int): The ID of the todo item to toggle.

        Returns:
            Todo: A Todo object representing the updated todo item.

        Raises:
            Exception: If the todo item is not found or if there's an error while updating the todo in the database.
        """
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

    @staticmethod
    async def delete_todo(id: int) -> bool:
        """
        Delete a todo item from the database.

        This function finds a todo item by its ID and deletes it from the database.

        Args:
            id (int): The ID of the todo item to delete.

        Returns:
            bool: True if the todo item was successfully deleted, False otherwise.

        Raises:
            Exception: If the todo item is not found or if there's an error while deleting the todo from the database.
        """
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
