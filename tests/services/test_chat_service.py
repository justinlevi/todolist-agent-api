import pytest
from src.services.chat_service import get_models, get_model_by_id, generate_chat_completion
from src.models.chat import ChatCompletionRequest, Message

@pytest.mark.asyncio
async def test_get_models():
    models = await get_models()
    assert len(models) > 0
    assert all(model.id for model in models)

@pytest.mark.asyncio
async def test_get_model_by_id():
    model = await get_model_by_id("default")
    assert model is not None
    assert model.id == "default"

    non_existent_model = await get_model_by_id("non-existent-model")
    assert non_existent_model is None

@pytest.mark.asyncio
async def test_generate_chat_completion(mock_chat_service):
    request = ChatCompletionRequest(
        model="default",
        messages=[Message(role="user", content="Hello, how are you?")]
    )
    response = await generate_chat_completion(request)
    assert response.id is not None
    assert response.model == request.model
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert response.choices[0].message.role == "assistant"
