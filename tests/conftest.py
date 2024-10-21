import os

# Set environment variables before importing settings and app
os.environ['ENVIRONMENT'] = 'test'
os.environ['API_KEY'] = 'test-api-key'

import pytest
import time
from fastapi.testclient import TestClient
from src.main import app
from src.config import settings
from src.services.chat_service import get_models, get_model_by_id, generate_chat_completion
from src.models.chat import (
    Model,
    ChatCompletionResponse,
    ChatCompletionChoice,
    Message,
    Usage,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta
)

@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    settings.ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def api_key_headers():
    return {"Authorization": f"Bearer {settings.API_KEY}"}

@pytest.fixture
def client():
    return TestClient(app, base_url="http://testserver")

@pytest.fixture
def mock_chat_service(mocker):
    # Mock models list to include 'default'
    mock_models = [
        Model(id="default", object="model", created=1234567890, owned_by="test"),
        # Add other models if necessary
    ]

    # Mock get_models to return mock_models
    async def mock_get_models():
        return mock_models

    mocker.patch('src.services.chat_service.get_models', side_effect=mock_get_models)

    # Mock get_model_by_id to return a model if it exists in mock_models
    async def mock_get_model_by_id(model_id):
        for model in mock_models:
            if model.id == model_id:
                return model
        return None

    mocker.patch('src.services.chat_service.get_model_by_id', side_effect=mock_get_model_by_id)

    # Mock generate_chat_completion to return a simulated response
    async def mock_generate_chat_completion(request):
        if request.stream:
            async def stream_response():
                for i in range(5):
                    yield ChatCompletionChunk(
                        id=f"chunk-{i}",
                        object="chat.completion.chunk",
                        created=int(time.time()),
                        model=request.model,
                        choices=[
                            ChatCompletionChunkChoice(
                                index=0,
                                delta=ChatCompletionChunkDelta(
                                    content=f"Chunk {i + 1} of the response",
                                    role="assistant" if i == 0 else None
                                ),
                                finish_reason=None
                            )
                        ]
                    )
            return stream_response()
        else:
            return ChatCompletionResponse(
                id="test-completion",
                object="chat.completion",
                created=int(time.time()),
                model=request.model,
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=Message(role="assistant", content="Hello! How can I assist you today?"),
                        finish_reason="stop"
                    )
                ],
                usage=Usage(prompt_tokens=5, completion_tokens=5, total_tokens=10)
            )

    mocker.patch(
        'src.services.chat_service.generate_chat_completion',
        side_effect=mock_generate_chat_completion
    )

@pytest.fixture
def sample_messages():
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]

