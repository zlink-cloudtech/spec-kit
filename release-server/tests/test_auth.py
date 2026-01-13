import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from release_server.auth import verify_token
from release_server.config import get_settings, Settings
from pydantic import SecretStr

app = FastAPI()

@app.get("/protected", dependencies=[Depends(verify_token)])
def protected_route():
    return {"status": "ok"}

client = TestClient(app)

@pytest.fixture
def mock_settings():
    def get_override():
        return Settings(auth_token=SecretStr("secret-token-123"), storage_path="/tmp/data")
    app.dependency_overrides[get_settings] = get_override
    yield
    app.dependency_overrides = {}

def test_auth_success(mock_settings):
    response = client.get("/protected", headers={"Authorization": "Bearer secret-token-123"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_invalid_token(mock_settings):
    response = client.get("/protected", headers={"Authorization": "Bearer wrong-token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication token"

def test_auth_missing_header(mock_settings):
    response = client.get("/protected")
    # HTTPBearer returns 403 if valid credentials are not provided (depending on auto_error=True default)
    # But sometimes 401. Allow both.
    assert response.status_code in (401, 403)
