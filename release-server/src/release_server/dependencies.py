from fastapi import Depends
from release_server.config import get_settings, Settings
from release_server.storage import StorageService
from release_server.services.package_service import PackageService

def get_storage_service(settings: Settings = Depends(get_settings)) -> StorageService:
    return StorageService(root=settings.storage_path)

def get_package_service(
    storage: StorageService = Depends(get_storage_service),
    settings: Settings = Depends(get_settings)
) -> PackageService:
    return PackageService(storage=storage, max_packages=settings.max_packages)
