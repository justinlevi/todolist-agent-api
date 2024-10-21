import pytest
import json

@pytest.fixture
def chat_completion_payload():
    return {
        "model": "default",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
    }

def test_create_chat_completion(
    chat_completion_payload,
    client,
    api_key_headers,
    mock_chat_service
):
    response = client.post(
        "/v1/chat/completions",
        json=chat_completion_payload,
        headers=api_key_headers
    )
    assert response.status_code == 200
    assert "choices" in response.json()
    assert len(response.json()["choices"]) > 0

def test_create_chat_completion_invalid_payload(
    client,
    api_key_headers,
    mock_chat_service
):
    invalid_payload = {"model": "default"}  # Missing 'messages'
    response = client.post(
        "/v1/chat/completions",
        json=invalid_payload,
        headers=api_key_headers
    )
    assert response.status_code == 422  # Unprocessable Entity

def test_create_chat_completion_stream(
    chat_completion_payload,
    client,
    api_key_headers,
    mock_chat_service
):
    chat_completion_payload["stream"] = True
    with client as c:
        response = c.post(
            "/v1/chat/completions",
            json=chat_completion_payload,
            headers=api_key_headers
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        chunks = []
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8') if isinstance(line, bytes) else line
                if line.startswith("data: "):
                    if line.strip() == "data: [DONE]":
                        break
                    chunks.append(json.loads(line[6:]))

        assert len(chunks) > 0
        for chunk in chunks:
            assert 'choices' in chunk
            assert len(chunk['choices']) > 0
            assert 'delta' in chunk['choices'][0]
            assert 'content' in chunk['choices'][0]['delta']

# Uncomment this test if you want to test unauthorized access
# def test_create_chat_completion_unauthorized(
#     client,
#     mock_chat_service
# ):
#     request_data = {
#         "model": "default",
#         "messages": [{"role": "user", "content": "Hello, how are you?"}]
#     }
#     response = client.post("/v1/chat/completions", json=request_data)
#     assert response.status_code == 403  # Unauthorized
