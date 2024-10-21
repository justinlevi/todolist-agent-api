import pytest
from src.graphql.schema import schema


@pytest.mark.asyncio
async def test_create_todo():
    query = """
    mutation {
        createTodo(title: "Test Todo") {
            id
            title
            completed
        }
    }
    """
    result = await schema.execute(query)
    assert result.errors is None
    assert result.data["createTodo"]["title"] == "Test Todo"
    assert result.data["createTodo"]["completed"] == False
