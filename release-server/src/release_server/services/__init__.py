from typing import List, Optional

class PackageMetadata:
    def __init__(self, name: str, path: str, size: int, created_at):
        self.name = name
        self.path = path
        self.size = size
        self.created_at = created_at
