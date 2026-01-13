import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile, HTTPException
from release_server.services.package_service import PackageService
from release_server.storage import PackageMetadata
from datetime import datetime

from datetime import datetime, timedelta

@pytest.fixture
def mock_storage():
    storage = AsyncMock()
    return storage

@pytest.fixture
def service(mock_storage):
    return PackageService(storage=mock_storage, max_packages=2)

@pytest.mark.asyncio
async def test_retention_policy_no_cleanup(service, mock_storage):
    # Setup 2 packages (equal to max)
    now = datetime.now()
    pkgs = [
        PackageMetadata(name="p1.zip", path="/p1", size=1, created_at=now),
        PackageMetadata(name="p2.zip", path="/p2", size=1, created_at=now - timedelta(hours=1))
    ]
    mock_storage.list_packages.return_value = pkgs
    
    deleted = await service.cleanup_old_packages()
    
    assert deleted == 0
    mock_storage.delete_package.assert_not_called()

@pytest.mark.asyncio
async def test_retention_policy_cleanup(service, mock_storage):
    # Setup 3 packages (max is 2)
    # create times: p1 (newest), p2 (middle), p3 (oldest)
    now = datetime.now()
    p1 = PackageMetadata(name="p1.zip", path="/p1", size=1, created_at=now)
    p2 = PackageMetadata(name="p2.zip", path="/p2", size=1, created_at=now - timedelta(hours=1))
    p3 = PackageMetadata(name="p3.zip", path="/p3", size=1, created_at=now - timedelta(hours=2))
    
    # Storage returns them in random order, service should sort them
    mock_storage.list_packages.return_value = [p2, p3, p1]
    
    deleted = await service.cleanup_old_packages()
    
    assert deleted == 1
    # Should delete p3 (oldest)
    mock_storage.delete_package.assert_called_once_with("p3.zip")

@pytest.mark.asyncio
async def test_retention_policy_multiple_cleanup(service, mock_storage):
    # Setup 4 packages (max is 2) -> should delete 2
    now = datetime.now()
    pkgs = [
        PackageMetadata(name=f"p{i}.zip", path=f"/p{i}", size=1, created_at=now - timedelta(hours=i))
        for i in range(4)
    ]
    # p0 is newest, p3 is oldest
    
    mock_storage.list_packages.return_value = pkgs
    
    deleted = await service.cleanup_old_packages()
    
    assert deleted == 2
    # Should delete p2 and p3
    assert mock_storage.delete_package.call_count == 2
    mock_storage.delete_package.assert_any_call("p2.zip")
    mock_storage.delete_package.assert_any_call("p3.zip")

@pytest.mark.asyncio
async def test_list_packages(service, mock_storage):
    mock_pkg = PackageMetadata(
        name="test.zip",
        path="/data/test.zip",
        size=123,
        created_at=datetime.now()
    )
    mock_storage.list_packages.return_value = [mock_pkg]
    
    result = await service.list_packages()
    assert len(result) == 1
    assert result[0].name == "test.zip"

@pytest.mark.asyncio
async def test_upload_package_success(service, mock_storage):
    file = MagicMock(spec=UploadFile)
    file.filename = "new.zip"
    file.read = AsyncMock(return_value=b"content")
    
    # Mock pre-existing files (none)
    mock_storage.list_packages.side_effect = [
        [], # First call (check exists)
        [PackageMetadata(name="new.zip", path="/data/new.zip", size=7, created_at=datetime.now())] # Second call (return metadata)
    ]
    
    result = await service.upload_package(file, overwrite=False)
    
    assert result.name == "new.zip"
    mock_storage.save_package.assert_called_once_with("new.zip", b"content")

@pytest.mark.asyncio
async def test_upload_conflict(service, mock_storage):
    file = MagicMock(spec=UploadFile)
    file.filename = "existing.zip"
    
    # Mock existing
    mock_storage.list_packages.return_value = [
        PackageMetadata(name="existing.zip", path="/path", size=1, created_at=datetime.now())
    ]
    
    with pytest.raises(HTTPException) as exc:
        await service.upload_package(file, overwrite=False)
    
    assert exc.value.status_code == 409
    mock_storage.save_package.assert_not_called()

@pytest.mark.asyncio
async def test_upload_overwrite(service, mock_storage):
    file = MagicMock(spec=UploadFile)
    file.filename = "existing.zip"
    file.read = AsyncMock(return_value=b"new-content")
    
    # Existing present
    mock_storage.list_packages.side_effect = [
        [PackageMetadata(name="existing.zip", path="/path", size=1, created_at=datetime.now())], # First call
        [PackageMetadata(name="existing.zip", path="/path", size=11, created_at=datetime.now())] # Second call
    ]
    
    result = await service.upload_package(file, overwrite=True)
    
    mock_storage.save_package.assert_called_once()
    assert result.size == 11
