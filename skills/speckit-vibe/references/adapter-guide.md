# Agent Adapter Development Guide

This guide explains how to add support for new AI agent CLIs to speckit-vibe.

## Overview

Speckit-vibe uses an adapter pattern to support multiple AI agents. Each adapter translates agent-agnostic workflow requests into agent-specific CLI commands.

```
┌─────────────────────────────────────────────────────────────┐
│                    speckit-vibe workflow                     │
│  (vibe_workflow.py / vibe_task.py)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    AgentAdapter (ABC)                        │
│  - build_command()                                          │
│  - execute()                                                │
│  - build_autonomous_suffix()                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │  Copilot  │   │  Claude   │   │   Aider   │
    │  Adapter  │   │   Code    │   │  Adapter  │
    └───────────┘   └───────────┘   └───────────┘
```

## Directory Structure

```
scripts/
├── adapters/
│   ├── __init__.py       # Package exports
│   ├── base.py           # AgentAdapter ABC and data classes
│   ├── registry.py       # Adapter registration and lookup
│   ├── copilot.py        # GitHub Copilot adapter
│   └── my_agent.py       # Your new adapter
├── vibe_workflow.py      # Main workflow orchestrator
├── vibe_task.py          # Task executor
└── config-manager.py     # Configuration management
```

## Step 1: Create Adapter Class

Create a new file `scripts/adapters/my_agent.py`:

```python
"""
My Agent CLI adapter for speckit-vibe.

This adapter implements the AgentAdapter interface for My Agent CLI.
"""

from typing import List
import shutil

from .base import (
    AgentAdapter,
    AgentConfig,
    ExecutionContext,
    ExecutionMode,
    ToolPermissions,
)


class MyAgentAdapter(AgentAdapter):
    """
    My Agent CLI adapter.
    
    Translates speckit-vibe execution requests into My Agent CLI commands.
    """
    
    @property
    def name(self) -> str:
        """Unique identifier for this agent."""
        return "my-agent"
    
    @property
    def executable(self) -> str:
        """CLI executable name."""
        return "my-agent-cli"
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return "My Agent CLI adapter for autonomous coding"
    
    def is_available(self) -> bool:
        """Check if CLI is installed."""
        return shutil.which(self.executable) is not None
    
    def get_default_model(self) -> str:
        """Return default model for this agent."""
        return "my-default-model"
    
    def get_default_excluded_tools(self) -> List[str]:
        """Return default excluded tools."""
        # Always exclude speckit-vibe to prevent recursion
        return ["speckit-vibe"]
    
    def get_install_instructions(self) -> str:
        """Return installation instructions."""
        return (
            "My Agent CLI is not installed.\n"
            "To install:\n"
            "  pip install my-agent-cli\n"
            "  my-agent-cli auth login\n"
        )
    
    def build_autonomous_suffix(self, stage: str) -> str:
        """Build prompt suffix for autonomous execution."""
        suffix = "[AUTONOMOUS MODE] "
        suffix += "Do not ask questions. Make reasonable assumptions. "
        suffix += "Complete all work without confirmation."
        
        # Add stage-specific hints
        if stage == "implement":
            suffix += " Execute all tasks in dependency order."
        
        return suffix
    
    def build_command(
        self,
        context: ExecutionContext,
        config: AgentConfig,
        permissions: ToolPermissions
    ) -> List[str]:
        """
        Build command as list of arguments.
        
        This is the core method - translate agent-agnostic context
        into your agent's specific CLI format.
        """
        cmd = [self.executable]
        
        # Add model flag (agent-specific format)
        cmd.extend(["--model", config.model])
        
        # Add timeout
        cmd.extend(["--timeout", str(config.timeout_minutes * 60)])
        
        # Add tool permissions (translate to agent's format)
        if permissions.allow_all:
            cmd.append("--allow-all-tools")
        
        for tool in permissions.excluded_tools:
            cmd.extend(["--exclude", tool])
        
        # Add no-interaction flag for autonomous mode
        if context.no_ask_user:
            cmd.append("--no-prompt")
        
        # Add logging flags
        if context.debug_log_dir:
            cmd.extend(["--log-dir", context.debug_log_dir])
        
        # Build prompt based on mode
        prompt = self._build_prompt(context)
        cmd.extend(["--message", prompt])
        
        return cmd
    
    def _build_prompt(self, context: ExecutionContext) -> str:
        """Build prompt based on execution context."""
        if context.mode == ExecutionMode.STAGE:
            prompt = f"Execute speckit workflow stage: {context.stage}"
            if context.autonomous_suffix:
                prompt = f"{prompt}\n\n{context.autonomous_suffix}"
            return prompt
        
        elif context.mode == ExecutionMode.TASK:
            return (
                f"Execute task {context.task_id}:\n\n"
                f"{context.task_info}\n\n"
                f"Spec directory: {context.spec_dir}"
            )
        
        else:
            return context.prompt or ""
```

## Step 2: Register the Adapter

Edit `scripts/adapters/registry.py`:

```python
from .copilot import CopilotAdapter
from .my_agent import MyAgentAdapter  # Add import

# Register built-in adapters
AdapterRegistry.register(CopilotAdapter)
AdapterRegistry.register(MyAgentAdapter)  # Add registration
```

## Step 3: Add Default Configuration

Edit `scripts/config-manager.py`:

```python
DEFAULT_CONFIG: Dict[str, Any] = {
    "agent": "copilot",
    # ... other settings ...
    "agent_config": {
        "copilot": {
            "model": "claude-sonnet-4.5",
            "allow_all": True,
            "excluded_tools": ["skill(speckit-vibe)"],
            "allow_paths": [],
            "allow_urls": []
        },
        # Add your agent's default config
        "my-agent": {
            "model": "my-default-model",
            "allow_all_tools": True,
            "excluded_tools": ["speckit-vibe"],
            "custom_option": "default_value"
        }
    }
}
```

## Step 4: Document Configuration

Add documentation to `references/config-reference.md`:

```markdown
### My Agent Configuration

\`\`\`json
{
  "agent_config": {
    "my-agent": {
      "model": "my-default-model",
      "allow_all_tools": true,
      "excluded_tools": ["speckit-vibe"],
      "custom_option": "value"
    }
  }
}
\`\`\`

#### my-agent.model

**Type**: `string`
**Default**: `"my-default-model"`

The model to use for My Agent sessions.

#### my-agent.custom_option

**Type**: `string`
**Default**: `"default_value"`

Description of what this option does.
```

## AgentAdapter Interface Reference

### Required Abstract Methods

| Method | Description |
|--------|-------------|
| `name` | Property returning unique adapter identifier |
| `executable` | Property returning CLI executable name |
| `is_available()` | Check if CLI is installed |
| `get_default_model()` | Return default model name |
| `get_default_excluded_tools()` | Return default tool exclusions |
| `build_command()` | Build CLI command from context |
| `build_autonomous_suffix()` | Build prompt suffix for autonomous mode |

### Optional Methods (with defaults)

| Method | Default Behavior |
|--------|------------------|
| `description` | Returns `"{name} agent adapter"` |
| `get_install_instructions()` | Generic installation message |
| `validate_config()` | Basic validation (model, timeout, retry) |
| `execute()` | Uses subprocess with timeout handling |

### Data Classes

#### ExecutionContext

```python
@dataclass
class ExecutionContext:
    mode: ExecutionMode           # STAGE, TASK, or INTERACTIVE
    spec_dir: str                 # Path to spec directory
    stage: Optional[str]          # Stage name (for STAGE mode)
    task_id: Optional[str]        # Task ID (for TASK mode)
    task_info: Optional[str]      # Task description
    prompt: Optional[str]         # Custom prompt (INTERACTIVE mode)
    session_log_path: Optional[str]   # Path for session transcript
    debug_log_dir: Optional[str]  # Directory for debug logs
    no_ask_user: bool             # Whether to suppress prompts
    autonomous_suffix: str        # Autonomous mode instructions
```

#### AgentConfig

```python
@dataclass
class AgentConfig:
    model: str                    # Model name
    timeout_minutes: int          # Execution timeout
    retry_count: int              # Retry attempts
    log_level: str                # Log verbosity
    extra: Dict[str, Any]         # Agent-specific options
```

#### ToolPermissions

```python
@dataclass
class ToolPermissions:
    allow_all: bool               # Allow all tools
    allowed_tools: List[str]      # Explicit allowed tools
    excluded_tools: List[str]     # Tools to exclude
    allowed_paths: List[str]      # Allowed file paths
    allowed_urls: List[str]       # Allowed URLs
```

## Testing Your Adapter

### Unit Tests

Create `scripts/adapters/tests/test_my_agent.py`:

```python
import pytest
from adapters.my_agent import MyAgentAdapter
from adapters.base import ExecutionContext, ExecutionMode, AgentConfig, ToolPermissions

def test_adapter_name():
    adapter = MyAgentAdapter()
    assert adapter.name == "my-agent"

def test_build_command_stage_mode():
    adapter = MyAgentAdapter()
    context = ExecutionContext(
        mode=ExecutionMode.STAGE,
        spec_dir="/test/spec",
        stage="plan",
        no_ask_user=True,
    )
    config = AgentConfig(model="test-model", timeout_minutes=30)
    permissions = ToolPermissions(allow_all=True)
    
    cmd = adapter.build_command(context, config, permissions)
    
    assert "my-agent-cli" in cmd
    assert "--model" in cmd
    assert "test-model" in cmd
    assert "--no-prompt" in cmd

def test_is_available_when_not_installed():
    adapter = MyAgentAdapter()
    # Will return False unless my-agent-cli is actually installed
    # This is expected behavior
    result = adapter.is_available()
    assert isinstance(result, bool)
```

### Integration Tests

```bash
# Test adapter registration
python3 -c "from adapters import list_adapters; print(list_adapters())"

# Test command building (dry run)
python3 vibe_workflow.py --agent my-agent --dry-run --spec test.md
```

## Best Practices

### 1. Always Exclude Self

Include `speckit-vibe` (or equivalent) in `get_default_excluded_tools()` to prevent infinite recursion.

### 2. Handle Missing CLI Gracefully

```python
def is_available(self) -> bool:
    try:
        return shutil.which(self.executable) is not None
    except Exception:
        return False
```

### 3. Provide Clear Install Instructions

```python
def get_install_instructions(self) -> str:
    return (
        f"{self.name} is not installed.\n\n"
        "To install:\n"
        "  Step 1: ...\n"
        "  Step 2: ...\n\n"
        "For documentation: https://..."
    )
```

### 4. Validate Agent-Specific Config

```python
def validate_config(self, config: AgentConfig) -> List[str]:
    errors = super().validate_config(config)
    
    # Add agent-specific validations
    if config.extra.get("custom_option") == "invalid":
        errors.append("custom_option cannot be 'invalid'")
    
    return errors
```

### 5. Support All Execution Modes

Handle all three `ExecutionMode` values:
- `STAGE`: Workflow stage execution (specify, plan, etc.)
- `TASK`: Individual task from tasks.md
- `INTERACTIVE`: Q&A session with user

## Common Patterns

### Slash Commands (Copilot-style)

```python
def _build_prompt(self, context: ExecutionContext) -> str:
    if context.mode == ExecutionMode.STAGE:
        return f"/speckit.{context.stage} {context.autonomous_suffix}"
```

### Structured Prompts

```python
def _build_prompt(self, context: ExecutionContext) -> str:
    if context.mode == ExecutionMode.TASK:
        return f"""<task>
<id>{context.task_id}</id>
<description>{context.task_info}</description>
<spec_dir>{context.spec_dir}</spec_dir>
</task>

{context.autonomous_suffix}"""
```

### Environment Variables

```python
def build_command(self, context, config, permissions) -> List[str]:
    cmd = [self.executable]
    
    # Some CLIs use env vars instead of flags
    import os
    os.environ["MY_AGENT_MODEL"] = config.model
    os.environ["MY_AGENT_TIMEOUT"] = str(config.timeout_minutes * 60)
    
    cmd.extend(["run", context.prompt])
    return cmd
```

## Troubleshooting

### Adapter Not Found

```
Error: Unknown agent adapter: 'my-agent'
```

**Solution**: Ensure adapter is registered in `registry.py`:
```python
AdapterRegistry.register(MyAgentAdapter)
```

### CLI Not Available

```
Error: Agent 'my-agent' is not available
```

**Solution**: Check `is_available()` implementation and ensure CLI is in PATH.

### Command Execution Fails

Enable debug logging:
```bash
python3 vibe_workflow.py --agent my-agent --log-level DEBUG ...
```

Check the generated command in logs and test it manually.
