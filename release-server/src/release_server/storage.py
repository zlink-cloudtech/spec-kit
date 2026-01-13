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
            if entry.is_file():
                # Get stats
                stat = entry.stat()
                packages.append(PackageMetadata(
                    name=entry.name,
                    path=entry.path,
                    size=stat.st_size,
                    created_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc)
                ))
        return packages

    async def delete_package(self, filename: str) -> None:
        """
        Deletes a package.
        Raises FileNotFoundError if file does not exist.
        """
        file_path = self.root / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Package {filename} not found")
        
        # Async removal? os.remove is sync but fast. 
        # For strict async, we can run in executor, but for this level os.remove is usually acceptable 
        # unless under heavy load. `aiofiles.os.remove` exists in newer versions or use `os.remove`.
        # release-server deps include `aiofiles`. aiofiles.os might be available.
        # Let's check imports.
        import aiofiles.os
        await aiofiles.os.remove(file_path)

