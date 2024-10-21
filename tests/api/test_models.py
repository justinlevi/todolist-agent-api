import pytest
from src.main import app

def test_list_models(api_key_headers, client):
    response = client.get("/v1/models", headers=api_key_headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0

def test_get_model(api_key_headers, client, mock_chat_service):
    response = client.get("/v1/models/default", headers=api_key_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "default"

def test_get_non_existent_model(api_key_headers, client):
    response = client.get("/v1/models/non-existent-model", headers=api_key_headers)
    assert response.status_code == 404

# def test_unauthorized_access(client):
#     response = client.get("/v1/models")
#     assert response.status_code == 403

