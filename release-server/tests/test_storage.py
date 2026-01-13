import pytest
import shutil
from pathlib import Path
from release_server.storage import StorageService

@pytest.fixture
def storage_root(tmp_path):
    # Create a temporary directory for storage
    d = tmp_path / "data"
    d.mkdir()
    return d

@pytest.fixture
def storage_service(storage_root):
    return StorageService(root=storage_root)

@pytest.mark.asyncio
async def test_save_package(storage_service, storage_root):
    filename = "test-package.zip"
    content = b"fake-zip-content"
    
    saved_path = await storage_service.save_package(filename, content)
    
    assert saved_path == storage_root / filename
    assert saved_path.exists()
    assert saved_path.read_bytes() == content

@pytest.mark.asyncio
async def test_list_packages(storage_service, storage_root):
    # Create some dummy files
    (storage_root / "pkg1.zip").write_text("1")
    (storage_root / "pkg2.zip").write_text("2")
    
    packages = await storage_service.list_packages()
    
    # Sort by name to ensure stable order for comparison
    packages.sort(key=lambda p: p.name)
    
    assert len(packages) == 2
    assert packages[0].name == "pkg1.zip"
    assert packages[1].name == "pkg2.zip"
    # Basic check for attributes
    assert packages[0].size > 0
    assert packages[0].created_at is not None

@pytest.mark.asyncio
async def test_delete_package(storage_service, storage_root):
    filename = "to-be-deleted.zip"
    path = storage_root / filename
    path.write_text("content")
    
    assert path.exists()
    
    await storage_service.delete_package(filename)
    
    assert not path.exists()

@pytest.mark.asyncio
async def test_delete_non_existent_package(storage_service):
    # Should probably not raise an error, or raise FileNotFoundError
    # Let's assume idempotency (no error if missing) based on "delete" semantics usually
    # Or strict deletion.
    # T005 task doesn't specify. I'll assume idempotency for now, or check implementation details.
    # Let's implementation raise FileNotFoundError so caller can decide (404).
    with pytest.raises(FileNotFoundError):
        await storage_service.delete_package("missing.zip")
