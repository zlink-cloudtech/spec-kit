"""
Agent adapters for speckit-vibe workflow execution.

This module provides an abstraction layer for different AI agent CLIs,
allowing speckit-vibe to work with various agents (GitHub Copilot, Claude Code, etc.)
through a unified interface.

Usage:
    from adapters import get_adapter, list_adapters
    
    # Get specific adapter
    adapter = get_adapter("copilot")
    
    # List available adapters
    available = list_adapters()
"""

from .base import (
    AgentAdapter,
    AgentConfig,
    ExecutionContext,
    ExecutionMode,
    ExecutionResult,
    ToolPermissions,
)
from .registry import (
    AdapterRegistry, 
    get_adapter, 
    get_default_adapter,
    list_adapters
)

__all__ = [
    # Base classes
    "AgentAdapter",
    "AgentConfig",
    "ExecutionContext",
    "ExecutionMode",
    "ExecutionResult",
    "ToolPermissions",
    # Registry
    "AdapterRegistry",
    "get_adapter",
    "get_default_adapter",
    "list_adapters",
]
