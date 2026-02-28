"""
Adapter registry for speckit-vibe.

This module provides a registry pattern for managing agent adapters,
allowing dynamic registration and lookup of adapters by name.

Usage:
    from adapters.registry import get_adapter, list_adapters
    
    # Get adapter by name
    adapter = get_adapter("copilot")
    
    # List all available adapters
    available = list_adapters()
    # Returns: {"copilot": True, "claude-code": False}
"""

from typing import Dict, List, Optional, Type

from .base import AgentAdapter
from .copilot import CopilotAdapter


class AdapterRegistry:
    """
    Registry for agent adapters.
    
    Provides centralized management of adapter classes with
    lazy instantiation and availability checking.
    
    Usage:
        # Register a custom adapter
        @AdapterRegistry.register
        class MyAdapter(AgentAdapter):
            ...
        
        # Get adapter instance
        adapter = AdapterRegistry.get("my-adapter")
        
        # List available adapters
        available = AdapterRegistry.list_available()
    """
    
    _adapters: Dict[str, Type[AgentAdapter]] = {}
    _default_adapter: str = "copilot"
    
    @classmethod
    def register(cls, adapter_class: Type[AgentAdapter]) -> Type[AgentAdapter]:
        """
        Register an adapter class.
        
        Can be used as a decorator:
            @AdapterRegistry.register
            class MyAdapter(AgentAdapter):
                ...
        
        Args:
            adapter_class: AgentAdapter subclass to register
            
        Returns:
            The adapter class (for decorator use)
        """
        # Create temporary instance to get name
        try:
            instance = adapter_class()
            cls._adapters[instance.name] = adapter_class
        except Exception:
            # If instantiation fails, skip registration
            pass
        return adapter_class
    
    @classmethod
    def get(cls, name: str) -> Optional[AgentAdapter]:
        """
        Get adapter instance by name.
        
        Args:
            name: Adapter name (e.g., "copilot")
            
        Returns:
            AgentAdapter instance, or None if not found
        """
        if name in cls._adapters:
            return cls._adapters[name]()
        return None
    
    @classmethod
    def get_or_raise(cls, name: str) -> AgentAdapter:
        """
        Get adapter instance by name, raising if not found.
        
        Args:
            name: Adapter name
            
        Returns:
            AgentAdapter instance
            
        Raises:
            ValueError: If adapter not found
        """
        adapter = cls.get(name)
        if adapter is None:
            available = list(cls._adapters.keys())
            raise ValueError(
                f"Unknown agent adapter: '{name}'. "
                f"Available adapters: {available}"
            )
        return adapter
    
    @classmethod
    def get_default(cls) -> AgentAdapter:
        """
        Get the default adapter (copilot).
        
        Returns:
            Default AgentAdapter instance
        """
        adapter = cls.get(cls._default_adapter)
        if adapter is None:
            # Fallback to CopilotAdapter directly
            return CopilotAdapter()
        return adapter
    
    @classmethod
    def set_default(cls, name: str) -> None:
        """
        Set the default adapter name.
        
        Args:
            name: Adapter name to set as default
            
        Raises:
            ValueError: If adapter name is not registered
        """
        if name not in cls._adapters:
            raise ValueError(f"Cannot set default to unknown adapter: '{name}'")
        cls._default_adapter = name
    
    @classmethod
    def list_all(cls) -> List[str]:
        """
        List all registered adapter names.
        
        Returns:
            List of adapter names
        """
        return list(cls._adapters.keys())
    
    @classmethod
    def list_available(cls) -> Dict[str, bool]:
        """
        List all adapters with their availability status.
        
        Returns:
            Dict mapping adapter name to availability (True/False)
        """
        result = {}
        for name, adapter_cls in cls._adapters.items():
            try:
                instance = adapter_cls()
                result[name] = instance.is_available()
            except Exception:
                result[name] = False
        return result
    
    @classmethod
    def get_adapter_info(cls, name: str) -> Optional[Dict]:
        """
        Get detailed information about an adapter.
        
        Args:
            name: Adapter name
            
        Returns:
            Dict with adapter info, or None if not found
        """
        adapter = cls.get(name)
        if adapter is None:
            return None
        
        return {
            "name": adapter.name,
            "executable": adapter.executable,
            "description": adapter.description,
            "available": adapter.is_available(),
            "default_model": adapter.get_default_model(),
            "default_excluded_tools": adapter.get_default_excluded_tools(),
            "install_instructions": adapter.get_install_instructions(),
        }


# Register built-in adapters
AdapterRegistry.register(CopilotAdapter)


# Convenience functions for module-level access
def get_adapter(name: str) -> Optional[AgentAdapter]:
    """
    Get adapter instance by name.
    
    Args:
        name: Adapter name (e.g., "copilot")
        
    Returns:
        AgentAdapter instance, or None if not found
    """
    return AdapterRegistry.get(name)


def get_adapter_or_raise(name: str) -> AgentAdapter:
    """
    Get adapter instance by name, raising if not found.
    
    Args:
        name: Adapter name
        
    Returns:
        AgentAdapter instance
        
    Raises:
        ValueError: If adapter not found
    """
    return AdapterRegistry.get_or_raise(name)


def get_default_adapter() -> AgentAdapter:
    """
    Get the default adapter.
    
    Returns:
        Default AgentAdapter instance
    """
    return AdapterRegistry.get_default()


def list_adapters() -> Dict[str, bool]:
    """
    List all adapters with their availability status.
    
    Returns:
        Dict mapping adapter name to availability (True/False)
    """
    return AdapterRegistry.list_available()


def adapter_info(name: str) -> Optional[Dict]:
    """
    Get detailed information about an adapter.
    
    Args:
        name: Adapter name
        
    Returns:
        Dict with adapter info, or None if not found
    """
    return AdapterRegistry.get_adapter_info(name)
