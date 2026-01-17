import os
import aiofiles
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class PackageMetadata(BaseModel):
    name: str
    path: str
    size: int
    created_at: datetime
    sha256: Optional[str] = Field(default=None, description="SHA256 checksum of the package content")
    # URL is dynamic, maybe handled by router, but storage just gives raw metadata
    
    @property
    def file_path(self) -> Path:
        return Path(self.path)

class StorageService:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    async def save_package(self, filename: str, content: bytes) -> Path:
        """
        Saves a package to the storage.
        Overwrites if exists.
        """
        file_path = self.root / filename
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        return file_path

    async def list_packages(self) -> List[PackageMetadata]:
        """
        Lists all packages in the storage.
        """
        packages = []
        if not self.root.exists():
            return []
            
        for entry in os.scandir(self.root):
            if entry.is_file() and not entry.name.endswith('.sha256'):
                # Get stats
                stat = entry.stat()
                checksum = await self.load_checksum(entry.name)
                packages.append(PackageMetadata(
                    name=entry.name,
                    path=entry.path,
                    size=stat.st_size,
                    created_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc),
                    sha256=checksum
                ))
        return packages

    async def delete_package(self, filename: str) -> None:
        """
        Deletes a package.
        Raises FileNotFoundError if file does not exist.
        """
        file_path = self.root / filename
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Package {filename} not found")
        
        # Async removal? os.remove is sync but fast. 
        # For strict async, we can run in executor, but for this level os.remove is usually acceptable 
        # unless under heavy load. `aiofiles.os.remove` exists in newer versions or use `os.remove`.
        # release-server deps include `aiofiles`. aiofiles.os might be available.
        # Let's check imports.
        import aiofiles.os
        await aiofiles.os.remove(file_path)

    async def save_checksum(self, filename: str, checksum: str) -> None:
        """
        Saves the checksum for a package in a sidecar file.
        """
        checksum_path = self.root / f"{filename}.sha256"
        async with aiofiles.open(checksum_path, "w") as f:
            await f.write(checksum)

    async def load_checksum(self, filename: str) -> Optional[str]:
        """
        Loads the checksum from the sidecar file if it exists.
        Returns None if no checksum file exists.
        """
        checksum_path = self.root / f"{filename}.sha256"
        # Check existence using aiofiles.os.path.exists or just wrapping in try/except or sync check
        # self.root / filename is a Path object, default sync .exists() is fine.
        if not checksum_path.exists():
            return None
        
        async with aiofiles.open(checksum_path, "r") as f:
            content = await f.read()
            return content.strip()

