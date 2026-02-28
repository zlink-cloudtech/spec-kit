# Configuration Reference

Complete reference for `.speckit-vc.json` configuration options.

## Configuration File

Create `.speckit-vc.json` in your project root:

```json
{
  "agent": "copilot",
  "model": "claude-sonnet-4.5",
  "allow_tools": true,
  "excluded_tools": ["skill(speckit-vibe)"],
  "log_level": "INFO",
  "max_parallel": 3,
  "auto_learning": true,
  "agents_md_path": "AGENTS.md",
  "timeout_minutes": 30,
  "retry_count": 2,
  "session_isolation": true,
  "spec_vibes_dir": "spec-vibes",
  "agent_config": {
    "copilot": {
      "allow_paths": [],
      "allow_urls": []
    }
  }
}
```

## Configuration Structure

The configuration is organized in two layers:

1. **Base configuration** - Top-level keys that all adapters must handle:
   - `model`: AI model identifier (adapter-specific format)
   - `allow_tools`: Whether to allow all tools/capabilities
   - `excluded_tools`: Tools to exclude from execution
   
2. **Agent-specific settings** - Nested under `agent_config.<agent_name>` for truly agent-specific options like path permissions, URLs, etc.

This design allows easy extension to support new AI agents while maintaining consistent configuration across adapters.

---

## Base Configuration Options

These options are handled by all agent adapters, though each adapter may interpret them differently.

### agent

**Type**: `string`  
**Default**: `"copilot"`  
**Values**: `copilot` (more coming soon)

Selects which AI agent adapter to use for workflow execution.

**Available Adapters:**

| Agent | Status | Description |
|-------|--------|-------------|
| `copilot` | ✅ Supported | GitHub Copilot CLI |
| `claude-code` | 🚧 Planned | Anthropic Claude Code |
| `aider` | 🚧 Planned | Aider CLI |

To list available adapters and their installation status:

```bash
scripts/config-manager.py adapters
scripts/config-manager.py adapters --verbose
```

### model

**Type**: `string`  
**Default**: `"claude-sonnet-4.5"`

The AI model to use for agent sessions. Format is adapter-specific.

**Common values for Copilot:**
- `claude-sonnet-4.5` - Balanced performance and cost (recommended)
- `gpt-4o` - OpenAI GPT-4o
- `gpt-4-turbo` - OpenAI GPT-4 Turbo

**Future adapters will support their own model formats:**
- Claude Code: `claude-sonnet-4-20250514`
- Aider: `gpt-4o`, `claude-3-5-sonnet-20241022`

### allow_tools

**Type**: `boolean`  
**Default**: `true`

Whether to allow all tools/capabilities. Each adapter translates this to its own permissions system.

- **Copilot**: Uses `--allow-all` flag when `true`
- **Future adapters**: May interpret as `--dangerously-skip-permissions` or similar

When `false`, you must specify allowed capabilities via adapter-specific options (e.g., `allow_paths`, `allow_urls` for Copilot).

### excluded_tools

**Type**: `array of strings`  
**Default**: `["skill(speckit-vibe)"]`

Tools to exclude from agent sessions.

**Example:**
```json
{
  "excluded_tools": [
    "skill(speckit-vibe)",
    "shell(rm)",
    "MyMCP(dangerous_tool)"
  ]
}
```

**Common exclusions:**
- `skill(speckit-vibe)`: **Required** - prevents infinite recursion
- `shell(git push)`: Prevent accidental pushes
- `shell(rm -rf)`: Prevent dangerous deletions

**Note**: Tool name format is adapter-specific. Adapters translate this list to their own exclusion mechanisms.

---

## Workflow Settings

These options control workflow behavior and apply regardless of which agent is used.

### log_level

**Type**: `string`  
**Default**: `"INFO"`  
**Values**: `DEBUG`, `INFO`, `WARN`, `ERROR`

Controls verbosity of output messages.

| Level | Description |
|-------|-------------|
| DEBUG | All messages including internal state |
| INFO | Normal operation messages |
| WARN | Warning and error messages |
| ERROR | Error messages only |

### max_parallel

**Type**: `integer`  
**Default**: `3`  
**Range**: `1` - `10`

Maximum number of concurrent task executions during the implement phase. Only tasks marked with `[P]` run in parallel.

**Recommendations:**
- **1**: Sequential execution, safest for file conflicts
- **2-3**: Good balance for most projects
- **5+**: For large projects with independent tasks

### auto_learning

**Type**: `boolean`  
**Default**: `true`

Automatically collect learnings from session logs at session end.

When enabled:
- Session logs are parsed for errors and issues
- Learnings are categorized and stored in `.speckit-vc/learnings/`
- Run `learning-collector.py --update-agents` to apply to AGENTS.md

### agents_md_path

**Type**: `string`  
**Default**: `"AGENTS.md"`

Path to the AGENTS.md file where learnings are applied.

### timeout_minutes

**Type**: `integer`  
**Default**: `30`  
**Range**: `1` - `120`

Timeout for individual stage/task execution in minutes.

### retry_count

**Type**: `integer`  
**Default**: `2`  
**Range**: `0` - `5`

Number of times to retry a failed task before marking it as failed.

### session_isolation

**Type**: `boolean`  
**Default**: `true`

Whether to run each workflow stage in an isolated session.

**IMPORTANT**: Keep this `true` to prevent context explosion. Setting to `false` may cause issues with large projects.

### spec_vibes_dir

**Type**: `string`  
**Default**: `"spec-vibes"`

Base directory for storing vibe session directories. Each new vibe session creates a subdirectory like `spec-vibes/001-feature-name/`.

---

## Agent-Specific Options

Agent-specific configuration is nested under `agent_config.<agent_name>`. These are for truly agent-specific settings that don't apply universally.

### Copilot Configuration

```json
{
  "agent_config": {
    "copilot": {
      "allow_paths": [],
      "allow_urls": []
    }
  }
}
```

#### copilot.allow_paths

**Type**: `array of strings`  
**Default**: `[]`

Additional paths to allow copilot to access (when `allow_tools` is `false`).

**Example:**
```json
{
  "allow_paths": [
    "/path/to/project",
    "/shared/libraries"
  ]
}
```

#### copilot.allow_urls

**Type**: `array of strings`  
**Default**: `[]`

URLs that copilot is allowed to fetch from.

**Example:**
```json
{
  "allow_urls": [
    "https://api.example.com",
    "https://docs.example.com"
  ]
}
```

---

## Future Agent Configurations

When new agents are added, their configuration will follow the same pattern:

**Base configuration** (top-level, all agents handle these):
```json
{
  "agent": "claude-code",
  "model": "claude-sonnet-4-20250514",
  "allow_tools": false,
  "excluded_tools": ["skill(speckit-vibe)"]
}
```

**Agent-specific configuration** (nested, for agent-specific features):
```json
{
  "agent_config": {
    "claude-code": {
      "editor_integration": true,
      "git_auto_commit": false
    },
    "aider": {
      "test_cmd": "npm test",
      "auto_commits": true
    }
  }
}
```

Each adapter translates the base configuration to its own CLI arguments and provides sensible defaults.

---

## Managing Configuration

### Initialize

```bash
scripts/config-manager.py init
scripts/config-manager.py init --force  # Overwrite existing
```

### View Configuration

```bash
scripts/config-manager.py show
scripts/config-manager.py show --json
```

### Update Values

```bash
# Set a top-level value
scripts/config-manager.py set agent copilot
scripts/config-manager.py set max_parallel 5
scripts/config-manager.py set log_level DEBUG

# Note: For nested agent_config values, edit the JSON file directly
```

### Get Single Value

```bash
scripts/config-manager.py get agent
scripts/config-manager.py get max_parallel
```

### List Available Adapters

```bash
scripts/config-manager.py adapters
scripts/config-manager.py adapters --verbose
```

### Validate Configuration

```bash
scripts/config-manager.py validate
```

### Reset to Defaults

```bash
scripts/config-manager.py reset
scripts/config-manager.py reset --force  # Skip confirmation
```

---

## Extending to New Agents

To add support for a new AI agent:

1. **Create adapter class** in `scripts/adapters/` implementing `AgentAdapter`:

```python
# scripts/adapters/my_agent.py
from .base import AgentAdapter

class MyAgentAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "my-agent"
    
    @property
    def executable(self) -> str:
        return "my-agent-cli"
    
    def is_available(self) -> bool:
        return shutil.which("my-agent-cli") is not None
    
    # ... implement other abstract methods
```

2. **Register the adapter** in `scripts/adapters/registry.py`:

```python
from .my_agent import MyAgentAdapter
AdapterRegistry.register(MyAgentAdapter)
```

3. **Add default configuration** in `config-manager.py`:

```python
DEFAULT_CONFIG = {
    # ...
    "model": "default-model",
    "allow_tools": true,
    "excluded_tools": ["skill(speckit-vibe)"],
    "agent_config": {
        "copilot": { ... },
        "my-agent": {
            "custom_option": "value"
        }
    }
}
```

4. **Document the configuration** in this file.

See [adapter-guide.md](adapter-guide.md) for detailed instructions.

---

## Environment Variables

Configuration can be overridden via environment variables:

| Variable | Config Key |
|----------|------------|
| `SPECKIT_AGENT` | agent |
| `SPECKIT_LOG_LEVEL` | log_level |
| `SPECKIT_MAX_PARALLEL` | max_parallel |

Environment variables take precedence over config file values.

## Per-Project vs Global Configuration

- **Per-project**: Place `.speckit-vc.json` in project root (recommended)
- **Global**: Place in `~/.config/speckit-vibe/config.json`

Per-project config takes precedence over global config.
