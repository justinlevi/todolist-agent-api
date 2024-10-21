from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine,
    select,
    Integer,
    String,
    Boolean,
    DateTime,
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
from datetime import datetime
from phi.tools.toolkit import Toolkit

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

    def get_todos(self) -> str:
        with Session(self.engine) as session:
            stmt = select(Todo)
            todos = session.execute(stmt).scalars().all()

            result = ""
            for todo in todos:
                result += f"ID: {todo.id}, Title: {todo.title}, Completed: {todo.completed}, Created At: {todo.created_at}, Due Date: {todo.due_date}, Weight: {todo.weight}, Parent ID: {todo.parentId}, Tags: {todo.tags}\n"
            return result

    def create_todo(
        self,
        title: str,
        due_date: Optional[str] = None,
        weight: int = 1,
        parent_id: Optional[int] = None,
        tags: Optional[str] = None,
    ) -> str:
        try:
            session = self.SessionLocal()
            new_todo = Todo(
                title=title,
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
            return f"Created Todo - ID: {new_todo.id}, Title: {new_todo.title}, Completed: {new_todo.completed}, Created At: {new_todo.created_at}, Due Date: {new_todo.due_date}, Weight: {new_todo.weight}, Parent ID: {new_todo.parentId}, Tags: {new_todo.tags}"
        except Exception as e:
            return f"Failed to create todo: {str(e)}"
        finally:
            session.close()

    def update_todo(
        self,
        id: int,
        title: Optional[str] = None,
        due_date: Optional[str] = None,
        weight: Optional[int] = None,
        parent_id: Optional[int] = None,
        tags: Optional[str] = None,
    ) -> str:
        try:
            session = self.SessionLocal()
            todo = session.query(Todo).filter(Todo.id == id).first()
            if todo is None:
                return f"Todo with id {id} not found"

            if title is not None:
                todo.title = title
            if due_date is not None:
                todo.dueDate = int(datetime.fromisoformat(due_date).timestamp() * 1000)
            if weight is not None:
                todo.weight = weight
            if parent_id is not None:
                todo.parentId = parent_id
            if tags is not None:
                todo.tags = tags

            session.commit()
            session.refresh(todo)
            return f"Updated Todo - ID: {todo.id}, Title: {todo.title}, Completed: {todo.completed}, Created At: {todo.created_at}, Due Date: {todo.due_date}, Weight: {todo.weight}, Parent ID: {todo.parentId}, Tags: {todo.tags}"
        except Exception as e:
            return f"Failed to update todo: {str(e)}"
        finally:
            session.close()

    def toggle_todo(self, id: int) -> str:
        try:
            session = self.SessionLocal()
            todo = session.query(Todo).filter(Todo.id == id).first()
            if todo is None:
                return f"Todo with id {id} not found"
            todo.completed = not todo.completed
            session.commit()
            session.refresh(todo)
            return f"Updated Todo - ID: {todo.id}, Title: {todo.title}, Completed: {todo.completed}, Created At: {todo.created_at}, Due Date: {todo.due_date}, Weight: {todo.weight}, Parent ID: {todo.parentId}, Tags: {todo.tags}"
        except Exception as e:
            return f"Failed to toggle todo: {str(e)}"
        finally:
            session.close()

    def delete_todo(self, id: int) -> str:
        try:
            session = self.SessionLocal()
            todo = session.query(Todo).filter(Todo.id == id).first()
            if todo is None:
                return f"Todo with id {id} not found"
            session.delete(todo)
            session.commit()
            return f"Successfully deleted todo with ID: {id}"
        except Exception as e:
            return f"Failed to delete todo: {str(e)}"
        finally:
            session.close()
