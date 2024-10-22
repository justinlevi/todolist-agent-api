import logging
from typing import List, Optional
from datetime import datetime
from prisma import Prisma
from src.models.todo import Todo, TodoCreate, TodoUpdate


logger = logging.getLogger(__name__)


class TodoNotFoundError(Exception):
    pass


class TodoCreationError(Exception):
    pass


class TodoUpdateError(Exception):
    pass


class TodoDeletionError(Exception):
    pass


class TodosService:
    def __init__(self, db: Prisma):
        self.db = db

    @staticmethod
    def _prisma_todo_to_model(todo):
        return Todo(
            id=todo.id,
            title=todo.title,
            completed=todo.completed,
            createdAt=todo.createdAt,
            dueDate=todo.dueDate,
            weight=todo.weight,
            parentId=todo.parentId,
            children=[child.id for child in (todo.children or [])],
            tags=todo.tags.split(",") if todo.tags else [],
        )

    async def get_todos(self) -> List[Todo]:
        """
        Retrieve all todos from the database.

        This function fetches all todo items stored in the database and returns them as a list of Todo objects.

        Returns:
            List[Todo]: A list of Todo objects representing all the todos in the database.

        Raises:
            Exception: If there's an error while fetching the todos from the database.
        """
        try:
            todos = await self.db.todo.find_many(include={"children": True})
            return [self._prisma_todo_to_model(todo) for todo in todos]
        except Exception as e:
            logger.error(f"Failed to fetch todos: {str(e)}")
            raise Exception(f"Failed to fetch todos: {str(e)}")

    async def create_todo(self, todo_data: TodoCreate) -> Todo:
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
        logger.info(f"Creating new todo: {todo_data}")
        try:
            todo = await self.db.todo.create(
                data={
                    "title": todo_data.title,
                    "dueDate": todo_data.dueDate,
                    "weight": todo_data.weight,
                    "parentId": todo_data.parentId,
                    "tags": ",".join(todo_data.tags),
                }
            )
            logger.info(f"Successfully created todo with id: {todo.id}")
            return Todo(
                id=todo.id,
                title=todo.title,
                completed=todo.completed,
                createdAt=todo.createdAt,
                dueDate=todo.dueDate,
                weight=todo.weight,
                parentId=todo.parentId,
                children=[],
                tags=todo_data.tags,
            )
        except Exception as e:
            logger.error(f"Failed to create todo: {str(e)}")
            raise TodoCreationError(f"Failed to create todo: {str(e)}")

    async def toggle_todo(self, id: int) -> Todo:
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
            todo = await self.db.todo.find_unique(
                where={"id": id}, include={"children": True}
            )
            if todo is None:
                raise TodoNotFoundError(f"Todo with id {id} not found")
            updated_todo = await self.db.todo.update(
                where={"id": id},
                data={"completed": not todo.completed},
                include={"children": True},
            )
            if updated_todo is None:
                raise TodoUpdateError(f"Failed to update todo with id {id}")
            return self._prisma_todo_to_model(updated_todo)
        except Exception as e:
            logger.error(f"Failed to toggle todo: {str(e)}")
            raise Exception(f"Failed to toggle todo: {str(e)}")

    async def delete_todo(self, id: int) -> bool:
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
            todo = await self.db.todo.find_unique(where={"id": id})
            if todo is None:
                raise TodoNotFoundError(f"Todo with id {id} not found")

            deleted_todo = await self.db.todo.delete(where={"id": id})
            if deleted_todo is None:
                raise TodoDeletionError(f"Failed to delete todo with id {id}")

            return True
        except Exception as e:
            logger.error(f"Failed to delete todo: {str(e)}")
            raise Exception(f"Failed to delete todo: {str(e)}")

    async def update_todo(self, id: int, todo_data: TodoUpdate) -> Todo:
        """
        Update a todo item in the database.

        This function updates an existing todo item with the given data.

        Args:
            id (int): The ID of the todo item to update.
            todo_data (TodoUpdate): The data to update the todo item with.

        Returns:
            Todo: A Todo object representing the updated todo item.

        Raises:
            Exception: If the todo item is not found or if there's an error while updating the todo in the database.
        """
        try:
            todo = await self.db.todo.find_unique(where={"id": id})
            if todo is None:
                raise TodoNotFoundError(f"Todo with id {id} not found")

            update_data = {
                k: v for k, v in todo_data.model_dump().items() if v is not None
            }
            if "tags" in update_data:
                update_data["tags"] = ",".join(update_data["tags"])

            updated_todo = await self.db.todo.update(
                where={"id": id},
                data=update_data,
                include={"children": True},
            )

            return self._prisma_todo_to_model(updated_todo)
        except Exception as e:
            logger.error(f"Failed to update todo: {str(e)}")
            raise Exception(f"Failed to update todo: {str(e)}")
