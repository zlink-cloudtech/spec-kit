import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml
from pydantic import SecretStr, field_validator
from pydantic.fields import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a YAML file
    at the project's root.
    """
    return _load_yaml_config()

def _load_yaml_config() -> Dict[str, Any]:
    # Default to standard path if env var is not set
    config_path = os.getenv("CONFIG_PATH", "/etc/release-server/config.yaml")
    
    path = Path(config_path)
    if not path.exists():
        return {}

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

class CustomYamlSource:
    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return _load_yaml_config()

yaml_source = CustomYamlSource()



class Settings(BaseSettings):
    """
    Application settings.
    Loads from environment variables and optionally a YAML file located at CONFIG_PATH.
    Environment variables take precedence over YAML values if both are present 
    (depending on the implementation of settings_customise_sources, but usually 
    env vars are higher priority than file).
    """
    
    # Core settings
    storage_path: Path = Field(default=Path("/data"), description="Path to store package files")
    max_packages: int = Field(default=10, description="Maximum number of packages to retain")
    auth_token: SecretStr = Field(..., description="Secret token for authentication")
    port: int = Field(default=8000, description="Port to listen on (for info only, uvicorn configures binding)")

    model_config = SettingsConfigDict(
        env_case_sensitive=False,
        env_file=".env",
        extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            yaml_source,
            file_secret_settings,
        )

    @field_validator("storage_path")
    @classmethod
    def ensure_path(cls, v: Path) -> Path:
        # We don't create it here to avoid side effects during import, 
        # but we could validte it looks like a path.
        return v

try:
    # Try to instantiate settings to fail early if missing required config
    # But allow import without failing if we are in a test env lacking vars
    # We'll expose get_settings() for dependency injection
    pass
except Exception:
    pass

def get_settings() -> Settings:
    """Factory for settings instance."""
    return Settings()
