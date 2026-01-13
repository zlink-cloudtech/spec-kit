import pytest
from typing import Generator
from fastapi.testclient import TestClient
from release_server.main import app
from release_server.config import get_settings, Settings
from pathlib import Path
from pydantic import SecretStr

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("AUTH_TOKEN", "test-secret")

@pytest.fixture
def test_settings(tmp_path: Path):
    # Override settings for test
    return Settings(
        storage_path=tmp_path / "data",
        auth_token=SecretStr("test-secret"),
        max_packages=5
    )

@pytest.fixture
def client(test_settings: Settings) -> Generator[TestClient, None, None]:
    # Dependency override
    app.dependency_overrides[get_settings] = lambda: test_settings
    
    with TestClient(app) as c:
        yield c
    
    # Cleanup done by tmp_path fixture
    app.dependency_overrides.clear()
