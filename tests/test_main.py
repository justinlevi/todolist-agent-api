from fastapi.testclient import TestClient
from src.main import app

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Chatbot API"}

def test_cors(client):
    response = client.options(
        "/v1/models",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"  # Use the appropriate method for the endpoint
        }
    )
    assert response.status_code in [200, 204]
    assert "Access-Control-Allow-Origin" in response.headers
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"

def test_security_headers(client):
    response = client.get("/")
    assert "X-XSS-Protection" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "X-Content-Type-Options" in response.headers
    assert "Strict-Transport-Security" in response.headers

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    # Optionally, check the other fields if needed
    assert "version" in data
    assert "timestamp" in data
