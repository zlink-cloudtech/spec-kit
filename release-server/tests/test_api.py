from fastapi import status

def test_upload_package_success(client, test_settings):
    file_content = b"test content"
    filename = "test_package.tar.gz"
    response = client.post(
        "/upload",
        files={"file": (filename, file_content, "application/gzip")},
        headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == filename
    assert data["size"] == len(file_content)
    
    # Verify storage
    saved_path = test_settings.storage_path / filename
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content

def test_upload_package_unauthorized(client):
    file_content = b"test content"
    response = client.post(
        "/upload",
        files={"file": ("test_package.tar.gz", file_content, "application/gzip")}
        # No auth header
    )
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

def test_upload_package_conflict(client):
    # First upload
    file_content = b"test content"
    client.post(
        "/upload",
        files={"file": ("conflict.tar.gz", file_content, "application/gzip")},
        headers={"Authorization": "Bearer test-secret"}
    )
    
    # Second upload without overwrite
    response = client.post(
        "/upload",
        files={"file": ("conflict.tar.gz", b"new content", "application/gzip")},
        headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == status.HTTP_409_CONFLICT

def test_upload_package_overwrite(client, test_settings):
    # First upload
    file_content = b"original content"
    filename = "overwrite.tar.gz"
    client.post(
        "/upload",
        files={"file": (filename, file_content, "application/gzip")},
        headers={"Authorization": "Bearer test-secret"}
    )
    
    # Verify first upload
    saved_path = test_settings.storage_path / filename
    assert saved_path.read_bytes() == file_content
    
    # Second upload with overwrite
    new_content = b"new content"
    response = client.post(
        "/upload?overwrite=true",
        files={"file": (filename, new_content, "application/gzip")},
        headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["size"] == len(new_content)
    
    # Verify overwritten content
    assert saved_path.read_bytes() == new_content

def test_get_latest_release(client, test_settings):
    # Setup: Create some dummy files directly in storage
    storage_path = test_settings.storage_path
    storage_path.mkdir(parents=True, exist_ok=True)
    
    file1 = storage_path / "pkg1.zip"
    file1.write_bytes(b"content1")
    
    file2 = storage_path / "pkg2.zip"
    file2.write_bytes(b"content2")
    
    response = client.get("/latest")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["tag_name"] == "latest"
    assert len(data["assets"]) == 2
    
    # Check assets
    asset_names = {a["name"] for a in data["assets"]}
    assert "pkg1.zip" in asset_names
    assert "pkg2.zip" in asset_names
    
    # Check URLs
    for asset in data["assets"]:
        assert asset["browser_download_url"].endswith(f"/assets/{asset['name']}")
        assert asset["size"] == len(b"content1") # since both same len

def test_delete_package_success(client, test_settings):
    # Setup: Upload a package first
    file_content = b"to_be_deleted"
    filename = "delete_me.tar.gz"
    client.post(
        "/upload",
        files={"file": (filename, file_content, "application/gzip")},
        headers={"Authorization": "Bearer test-secret"}
    )
    
    # Verify it exists
    saved_path = test_settings.storage_path / filename
    assert saved_path.exists()
    
    # Delete it
    response = client.delete(
        f"/assets/{filename}",
        headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's gone
    assert not saved_path.exists()
    
    # Verify it's gone from list
    list_response = client.get("/latest")
    assets = list_response.json()["assets"]
    assert filename not in [a["name"] for a in assets]

def test_delete_package_not_found(client):
    response = client.delete(
        "/assets/non_existent_package.tar.gz",
        headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_package_unauthorized(client):
    response = client.delete("/assets/any_package.tar.gz")
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


def test_download_asset_success(client, test_settings):
    # Setup
    filename = "download_test.zip"
    content = b"downloadable content"
    test_settings.storage_path.mkdir(parents=True, exist_ok=True)
    (test_settings.storage_path / filename).write_bytes(content)
    
    response = client.get(f"/assets/{filename}")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == content
    assert response.headers["content-disposition"] == f'attachment; filename="{filename}"'

def test_download_asset_not_found(client):
    response = client.get("/assets/non_existent.zip")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == status.HTTP_200_OK
    assert response.text == "OK"

def test_readyz(client):
    response = client.get("/readyz")
    assert response.status_code == status.HTTP_200_OK
    assert response.text == "OK"
