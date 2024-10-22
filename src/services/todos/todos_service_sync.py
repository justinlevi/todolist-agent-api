from typing import List, Optional
from datetime import datetime
from sqlalchemy import (
    create_engine,
    select,
    Integer,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import (
    Session,
    Mapped,
    mapped_column,
    declarative_base,
    sessionmaker,
    relationship,
)
from phi.tools.toolkit import Toolkit
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Todo(Base):
    __tablename__ = "Todo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    createdAt: Mapped[int] = mapped_column(Integer)
    dueDate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight: Mapped[int] = mapped_column(Integer, default=1)
    parentId: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("Todo.id"), nullable=True
    )
    tags: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    parent = relationship("Todo", remote_side=[id], backref="children")

    @property
    def created_at(self):
        return datetime.fromtimestamp(self.createdAt / 1000)

    @property
    def due_date(self):
        return datetime.fromtimestamp(self.dueDate / 1000) if self.dueDate else None

    def __repr__(self):
        return f"<Todo(id={self.id}, title='{self.title}', completed={self.completed}, createdAt={self.created_at}, dueDate={self.due_date}, weight={self.weight}, parentId={self.parentId}, tags={self.tags})>"


class TodosServiceSync(Toolkit):
    def __init__(self, db_url: str):
        super().__init__(name="todos_service_sync")
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        Base.metadata.create_all(bind=self.engine)

        self.register(self.get_todos)
        self.register(self.create_todo)
        self.register(self.update_todo)
        self.register(self.toggle_todo)
        self.register(self.delete_todo)
        self.register(self.filter_todos)

    def get_todos(self) -> str:
        """
        Retrieve all todos from the database.

        Returns:
            str: A string representation of all todos, with each todo on a new line.
        """
        logger.info("Fetching all todos")
        try:
            with Session(self.engine) as session:
                stmt = select(Todo)
                todos = session.execute(stmt).scalars().all()

                result = ""
                for todo in todos:
                    result += self._format_todo(todo) + "\n"
                logger.info(f"Successfully fetched {len(todos)} todos")
                return result
        except Exception as e:
            logger.error(f"Error fetching todos: {str(e)}", exc_info=True)
            return f"Error fetching todos: {str(e)}"

    def create_todo(
        self,
        title: str,
        completed: bool = False,
        due_date: Optional[str] = None,
        weight: int = 1,
        parent_id: Optional[int] = None,
        tags: Optional[str] = None,
    ) -> str:
        """
        Create a new todo item in the database.

        Args:
            title (str): The title of the new todo item.
            due_date (Optional[str]): The due date of the todo item in ISO format (YYYY-MM-DD).
            weight (int): The priority weight of the todo item (default: 1).
            parent_id (Optional[int]): The ID of the parent todo item, if any.
            tags (Optional[str]): Comma-separated list of tags for the todo item.

        Returns:
            str: A string representation of the created todo item.
        """
        logger.info(f"Creating new todo: {title}")
        try:
            with Session(self.engine) as session:
                new_todo = Todo(
                    title=title,
                    completed=completed,
                    createdAt=int(datetime.now().timestamp() * 1000),
                    dueDate=(
                        int(datetime.fromisoformat(due_date).timestamp() * 1000)
                        if due_date
                        else None
                    ),
                    weight=weight,
                    parentId=parent_id,
                    tags=tags,
                )
                session.add(new_todo)
                session.commit()
                session.refresh(new_todo)
                logger.info(f"Successfully created todo with ID: {new_todo.id}")
                return f"Created Todo: {self._format_todo(new_todo)}"
        except Exception as e:
            logger.error(f"Failed to create todo: {str(e)}", exc_info=True)
            return f"Failed to create todo: {str(e)}"

    def update_todo(
        self,
        id: int,
        title: Optional[str] = None,
        completed: Optional[bool] = None,
        due_date: Optional[str] = None,
        weight: Optional[int] = None,
        parent_id: Optional[int] = None,
        tags: Optional[str] = None,
    ) -> str:
        """
        Update an existing todo item in the database.

        Args:
            id (int): The ID of the todo item to update.
            title (Optional[str]): The new title of the todo item.
            due_date (Optional[str]): The new due date of the todo item in ISO format (YYYY-MM-DD).
            weight (Optional[int]): The new priority weight of the todo item.
            parent_id (Optional[int]): The new parent ID of the todo item.
            tags (Optional[str]): New comma-separated list of tags for the todo item.

        Returns:
            str: A string representation of the updated todo item.
        """
        logger.info(f"Updating todo with ID: {id}")
        try:
            with Session(self.engine) as session:
                todo = session.query(Todo).filter(Todo.id == id).first()
                if todo is None:
                    logger.warning(f"Todo with id {id} not found")
                    return f"Todo with id {id} not found"

                if title is not None:
                    todo.title = title
                if completed is not None:
                    todo.completed = completed
                if due_date is not None:
                    todo.dueDate = int(
                        datetime.fromisoformat(due_date).timestamp() * 1000
                    )
                if weight is not None:
                    todo.weight = weight
                if parent_id is not None:
                    todo.parentId = parent_id
                if tags is not None:
                    todo.tags = tags
                session.commit()
                session.refresh(todo)
                logger.info(f"Successfully updated todo with ID: {id}")
                return f"Updated Todo: {self._format_todo(todo)}"
        except Exception as e:
            logger.error(f"Failed to update todo: {str(e)}", exc_info=True)
            return f"Failed to update todo: {str(e)}"

    def toggle_todo(self, id: int) -> str:
        """
        Toggle the completion status of a todo item.

        Args:
            id (int): The ID of the todo item to toggle.

        Returns:
            str: A string representation of the toggled todo item.
        """
        logger.info(f"Toggling todo with ID: {id}")
        try:
            with Session(self.engine) as session:
                todo = session.query(Todo).filter(Todo.id == id).first()
                if todo is None:
                    logger.warning(f"Todo with id {id} not found")
                    return f"Todo with id {id} not found"
                todo.completed = not todo.completed
                session.commit()
                session.refresh(todo)
                logger.info(f"Successfully toggled todo with ID: {id}")
                return f"Toggled Todo: {self._format_todo(todo)}"
        except Exception as e:
            logger.error(f"Failed to toggle todo: {str(e)}", exc_info=True)
            return f"Failed to toggle todo: {str(e)}"

    def delete_todo(self, id: int) -> str:
        """
        Delete a todo item from the database.

        Args:
            id (int): The ID of the todo item to delete.

        Returns:
            str: A confirmation message of the deletion.
        """
        logger.info(f"Deleting todo with ID: {id}")
        try:
            with Session(self.engine) as session:
                todo = session.query(Todo).filter(Todo.id == id).first()
                if todo is None:
                    logger.warning(f"Todo with id {id} not found")
                    return f"Todo with id {id} not found"
                session.delete(todo)
                session.commit()
                logger.info(f"Successfully deleted todo with ID: {id}")
                return f"Successfully deleted todo with ID: {id}"
        except Exception as e:
            logger.error(f"Failed to delete todo: {str(e)}", exc_info=True)
            return f"Failed to delete todo: {str(e)}"

    def filter_todos(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tags: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> str:
        """
        Filter todos based on various criteria.

        Args:
            start_date (Optional[str]): Start date for filtering todos in ISO format (YYYY-MM-DD).
            end_date (Optional[str]): End date for filtering todos in ISO format (YYYY-MM-DD).
            tags (Optional[str]): Comma-separated list of tags to filter todos.
            completed (Optional[bool]): Filter todos by completion status (True/False).

        Returns:
            str: A string representation of the filtered todos, with each todo on a new line.
        """
        logger.info("Filtering todos")
        try:
            with Session(self.engine) as session:
                query = session.query(Todo)

                if start_date:
                    start_timestamp = int(
                        datetime.fromisoformat(start_date).timestamp() * 1000
                    )
                    query = query.filter(Todo.dueDate >= start_timestamp)

                if end_date:
                    end_timestamp = int(
                        datetime.fromisoformat(end_date).timestamp() * 1000
                    )
                    query = query.filter(Todo.dueDate <= end_timestamp)

                if tags:
                    tag_list = tags.split(",")
                    query = query.filter(Todo.tags.contains(tag_list[0]))
                    for tag in tag_list[1:]:
                        query = query.filter(Todo.tags.contains(tag))

                if completed is not None:
                    query = query.filter(Todo.completed == completed)

                todos = query.all()

                result = ""
                for todo in todos:
                    result += self._format_todo(todo) + "\n"
                logger.info(f"Successfully filtered {len(todos)} todos")
                return result
        except Exception as e:
            logger.error(f"Error filtering todos: {str(e)}", exc_info=True)
            return f"Error filtering todos: {str(e)}"

    def _format_todo(self, todo: Todo) -> str:
        """
        Format a todo item as a string.

        Args:
            todo (Todo): The todo item to format.

        Returns:
            str: A string representation of the todo item.
        """
        tags = todo.tags.split(",") if todo.tags else []
        return f"ID: {todo.id}, Title: {todo.title}, Completed: {todo.completed}, Created At: {todo.created_at}, Due Date: {todo.due_date}, Weight: {todo.weight}, Parent ID: {todo.parentId}, Tags: {tags}"
