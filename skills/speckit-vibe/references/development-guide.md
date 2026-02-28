# Development Guide

Guide for developing, extending, and debugging speckit-vibe itself.

---

## Architecture Overview

```
scripts/
├── vibe_workflow.py          # Main workflow orchestrator
├── vibe_task.py              # Individual task executor
├── config-manager.py         # Configuration management
├── state-tracker.py          # Workflow state persistence
├── learning-collector.py     # Learning extraction & AGENTS.md update
└── adapters/                 # Pluggable agent adapters
    ├── __init__.py
    ├── base.py               # AgentAdapter ABC
    ├── copilot.py            # GitHub Copilot adapter
    └── registry.py           # Adapter discovery & registration
```

---

## Adapter Pattern

Speckit-vibe uses a pluggable adapter pattern to support multiple AI agents.

### Adapter Class Hierarchy

```
┌─────────────────────────────────────────────┐
│           AgentAdapter (ABC)                 │
│  - name: str                                │
│  - build_command(context) -> List[str]      │
│  - execute(context) -> ExecutionResult      │
│  - build_autonomous_suffix() -> str         │
│  - get_capabilities() -> Dict               │
└──────────────────────┬──────────────────────┘
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Copilot   │ │   Claude    │ │   Future    │
    │   Adapter   │ │   Adapter   │ │   Adapters  │
    └─────────────┘ └─────────────┘ └─────────────┘
```

### Creating a New Adapter

See [🔧 Adapter Guide](adapter-guide.md) for complete instructions.

Quick steps:

1. Create `adapters/my_agent.py`
2. Implement `AgentAdapter` ABC
3. Register in `adapters/registry.py`
4. Test with `config-manager.py adapters`

---

## Code Style Guidelines

### Python Standards

- **Python 3.8+** compatibility (standard library only)
- **Type hints** for all public functions
- **Docstrings** for all classes and public methods
- **PEP 8** formatting

### Error Handling

All scripts should:

1. Log errors to `skill-errors.log` in the spec-vibes session directory
2. Return appropriate exit codes
3. Provide actionable error messages

```python
import logging
from pathlib import Path

def setup_skill_error_logging(spec_dir: Path) -> logging.Logger:
    """Setup logging to skill-errors.log in the session directory."""
    logger = logging.getLogger('speckit-vibe')
    handler = logging.FileHandler(spec_dir / 'skill-errors.log')
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] SKILL_ERROR: %(filename)s line %(lineno)d\n'
        'Message: %(message)s\n'
    ))
    logger.addHandler(handler)
    return logger
```

### State Persistence

- Use JSON files for state persistence
- Store in `.speckit-vc/` for global state
- Store in `spec-vibes/<session>/` for session state
- Never rely on environment variables for persistent state

---

## Testing

### Manual Testing

```bash
# Test workflow with dry-run
python3 scripts/vibe_workflow.py --dry-run --spec test/fixtures/SPECIFICATION.md

# Test individual script
python3 scripts/config-manager.py validate

# Test adapter discovery
python3 scripts/config-manager.py adapters --verbose
```

### Test Fixtures

Create test fixtures in `test/fixtures/`:

```
test/
└── fixtures/
    ├── SPECIFICATION.md     # Sample spec
    ├── tasks.md             # Sample tasks
    └── .speckit-vc.json     # Test config
```

---

## Debugging

### Enable Debug Logging

```bash
# Via command line
python3 scripts/vibe_workflow.py --log-level DEBUG ...

# Via config
python3 scripts/config-manager.py set log_level DEBUG
```

### View Session Transcripts

```bash
# Human-readable session transcript
cat spec-vibes/001-feature/sessions/stage_plan_*_session.md

# Detailed copilot logs with AI reasoning
grep "reasoning_text" spec-vibes/001-feature/copilot-logs/*.log
```

### View Skill Errors

```bash
# Skill-specific errors (bugs in scripts)
cat spec-vibes/001-feature/skill-errors.log
```

### Common Debug Scenarios

| Scenario | What to Check |
|----------|---------------|
| Stage not running | `state-tracker.py status` |
| Wrong adapter used | `config-manager.py show` |
| Tasks not found | Verify tasks.md format |
| Parallel issues | Check `[P]` markers in tasks.md |

---

## Contributing

### Adding a New Feature

1. **Create branch**: `feature/my-feature`
2. **Update SKILL.md** if new scenarios added
3. **Update references** if documentation changes
4. **Test manually** with dry-run
5. **Submit PR** with description

### Adding a New Script

1. Follow existing script patterns (argparse, logging, exit codes)
2. Add to [Scripts Reference](scripts-reference.md)
3. Add usage examples to SKILL.md if user-facing

### Modifying Workflow Stages

1. Update [Workflow Stages](workflow-stages.md) documentation
2. Update stage table in SKILL.md
3. Test with `--stage` option to verify isolation

---

## File Structure Reference

### Global State (`.speckit-vc/`)

```
.speckit-vc/
├── config.json           # Active config (copy of .speckit-vc.json)
├── state.json            # Current workflow state
├── sessions/             # Global session logs
├── learnings/            # Collected learnings
│   ├── pending.json      # Awaiting review
│   └── applied.json      # Already in AGENTS.md
└── tasks/                # Task execution status
```

### Session State (`spec-vibes/<session>/`)

```
spec-vibes/001-user-auth/
├── SPECIFICATION.md          # Requirements specification
├── spec.md                   # Generated spec
├── plan.md                   # Technical plan
├── tasks.md                  # Task list
├── checklists/               # Quality checklists
├── sessions/                 # Session transcripts
│   ├── stage_specify_*.log
│   └── stage_specify_*_session.md
├── copilot-logs/             # Detailed AI logs
│   └── process-*.log
└── skill-errors.log          # Skill-specific errors
```

---

## Related Documentation

- [🔧 Adapter Guide](adapter-guide.md) - Creating new agent adapters
- [📜 Scripts Reference](scripts-reference.md) - Script CLI documentation
- [📋 Configuration Reference](config-reference.md) - All config options
- [🔄 Workflow Stages](workflow-stages.md) - Stage details
- [📝 Task Format](task-format.md) - Task structure and markers
