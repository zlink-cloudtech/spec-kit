from typing import List, Optional
import hashlib
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from release_server.storage import StorageService, PackageMetadata

class PackageService:
    def __init__(self, storage: StorageService, max_packages: int = 10):
        self.storage = storage
        self.max_packages = max_packages

    async def list_packages(self) -> List[PackageMetadata]:
        # Sort by creation time descending (newest first)
        packages = await self.storage.list_packages()
        return sorted(packages, key=lambda p: p.created_at, reverse=True)

    async def cleanup_old_packages(self) -> int:
        """
        Enforce retention policy.
        Returns number of deleted packages.
        """
        packages = await self.list_packages() # Already sorted newest first
        if len(packages) <= self.max_packages:
            return 0
        
        to_delete = packages[self.max_packages:]
        deleted_count = 0
        for pkg in to_delete:
            try:
                await self.delete_package(pkg.name)
                deleted_count += 1
            except Exception:
                # Log error but continue
                pass
        return deleted_count

    async def get_package_path(self, filename: str) -> Path:
        """
        Gets the filesystem path for a package.
        Raises 404 if not found.
        """
        path = self.storage.root / filename
        if not path.exists() or not path.is_file():
            raise HTTPException(status_code=404, detail="Package not found")
        return path

    async def upload_package(self, file: UploadFile, overwrite: bool = False) -> PackageMetadata:
        """
        Uploads a package.
        If overwrite is False and file exists, raises 409 Conflict.
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename required")

        # Check existence if not overwriting
        # This is a bit racy but acceptable for this scale
        # Ideally storage should handle atomic creation or we check list
        # StorageService doesn't have `exists` method, let's list.
        # Or add `exists` to StorageService? T005 didn't explicit ask for it but it's useful.
        # Let's verify via existing list for now, or assume storage.save overwrites.
        # If overwrite=False, we should check.
        existing = await self.storage.list_packages()
        if not overwrite:
            if any(p.name == file.filename for p in existing):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Package {file.filename} already exists"
                )

        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file content")
        
        # Calculate checksum
        sha256_hash = hashlib.sha256(content).hexdigest()

        await self.storage.save_package(file.filename, content)
        await self.storage.save_checksum(file.filename, sha256_hash)
        
        # Return new metadata
        # We assume save is successful
        # We need to construct metadata. We can re-fetch just this one or all.
        # Re-listing is safest for mtime/size exactness.
        updated_list = await self.storage.list_packages()
        for p in updated_list:
            if p.name == file.filename:
                return p
        
        # Should not happen
        raise HTTPException(status_code=500, detail="Upload verification failed")

    async def delete_package(self, filename: str) -> None:
        try:
            await self.storage.delete_package(filename)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Package not found")
