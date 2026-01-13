from fastapi import status
import pytest

def test_list_packages_default_json(client, test_settings):
    # Setup: Create some dummy files
    storage_path = test_settings.storage_path
    storage_path.mkdir(parents=True, exist_ok=True)
    (storage_path / "pkg.zip").write_bytes(b"content")

    response = client.get("/packages")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "pkg.zip"

def test_list_packages_accept_html(client, test_settings):
    # Setup
    storage_path = test_settings.storage_path
    storage_path.mkdir(parents=True, exist_ok=True)
    (storage_path / "pkg.zip").write_bytes(b"content")

    response = client.get("/packages", headers={"Accept": "text/html"})
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]
    assert "<html" in response.text
    assert "pkg.zip" in response.text

def test_list_packages_query_json(client, test_settings):
    # Setup
    storage_path = test_settings.storage_path
    storage_path.mkdir(parents=True, exist_ok=True)
    (storage_path / "pkg.zip").write_bytes(b"content")

    # Even with Accept: text/html, query param should win
    response = client.get("/packages?format=json", headers={"Accept": "text/html"})
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert data[0]["name"] == "pkg.zip"

def test_list_packages_query_html(client, test_settings):
    # Setup
    storage_path = test_settings.storage_path
    storage_path.mkdir(parents=True, exist_ok=True)
    (storage_path / "pkg.zip").write_bytes(b"content")

    # Even with Accept: application/json, query param should win
    response = client.get("/packages?format=html", headers={"Accept": "application/json"})
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]
    assert "<html" in response.text
