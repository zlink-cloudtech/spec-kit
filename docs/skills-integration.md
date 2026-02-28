# Skills Integration in SpecKit

## Overview

SpecKit uses a **configuration-driven skill injection system** that automatically loads specialized skills into AI agent contexts based on the current development phase. This enables agents to adopt expert personas and follow domain-specific workflows without hardcoding skill logic into the core framework.

## Architecture

### The Adapter Pattern (Sidecar Model)

Skills in SpecKit follow a clean separation between:

1. **Generic Skill Definition** (`SKILL.md`): Pure prompt engineering that works with any AI agent
2. **SpecKit Integration** (`speckit-adapter.yaml`): Configuration that maps skills to lifecycle phases

This design keeps skills portable and reusable while allowing SpecKit-specific orchestration.

### Components

```text
skills/
├── speckit-architect/
│   ├── SKILL.md                  # Generic architecture skill
│   └── speckit-adapter.yaml      # SpecKit binding: phase=plan
├── speckit-developer/
│   ├── SKILL.md                  # Generic TDD skill
│   └── speckit-adapter.yaml      # SpecKit binding: phase=implement
└── speckit-tech-lead/
    ├── SKILL.md                  # Generic task planning skill
    └── speckit-adapter.yaml      # SpecKit binding: phase=tasks
```

## How It Works

### 1. Phase-Based Activation

When a SpecKit command runs (e.g., `/speckit.plan`), it:

1. Calls `scripts/bash/update-agent-context.sh <agent> <phase>`
2. The script invokes `scripts/resolve-skills.py <phase>`
3. The resolver scans `skills/*/speckit-adapter.yaml` for matching phases
4. Skills are injected into the agent context file (e.g., `CLAUDE.md`)

### 2. Skill Resolution

The `resolve-skills.py` script:

```python
# Pseudocode
for each skills/*/speckit-adapter.yaml:
    if hook.phase == requested_phase:
        load hook.context (usually SKILL.md)
        sort by hook.priority (descending)
        output skill content
```

### 3. Context Injection

Skills are appended to the agent context file after a marker:

```markdown
<!-- SPECKIT_ACTIVE_SKILLS -->

## Active Skills (Phase: plan)

The following specialist skills are active for this phase...

### Skill: speckit-architect
[SKILL.md content]
```

## Adapter Configuration Schema

**File**: `skills/<skill-name>/speckit-adapter.yaml`

```yaml
name: skill-name              # Unique identifier
hooks:
  - phase: plan               # Lifecycle phase (plan, tasks, implement, converge)
    priority: 100             # Sort order (higher = loaded first)
    context: SKILL.md         # Skill content file to inject
    instructions: |           # (Optional) SpecKit-specific orchestration instructions
      ## SpecKit Integration
      - These instructions are appended after SKILL.md content
      - Use for framework-specific paths and workflow bindings
      - Keeps SKILL.md portable while adapter provides the glue
```

### Supported Phases

| Phase | Purpose | Active Skills |
|-------|---------|---------------|
| `plan` | Architecture & design planning | `speckit-architect` |
| `tasks` | Task breakdown & decomposition | `speckit-tech-lead`, `speckit-developer` |
| `implement` | Code implementation | `speckit-developer` |
| `converge` | Documentation & system convergence | `speckit-librarian` |

### Priority Behavior

- Skills with **higher priority** are loaded **first**
- Default priority: `100`
- If two skills have the same priority, order is undefined

## Integration Points

### Command Templates

Skills are injected via the `agent_scripts` frontmatter in command templates:

**`templates/commands/plan.md`**:

```yaml
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__ plan
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__ -Phase plan
```

### Update Flow

```text
User runs: /speckit.plan
    ↓
templates/commands/plan.md executes
    ↓
{AGENT_SCRIPT} runs with phase=plan
    ↓
update-agent-context.sh calls resolve-skills.py plan
    ↓
CLAUDE.md (or agent file) updated with speckit-architect skill
    ↓
Agent adopts architect persona for planning
```

## Creating New Skills

### Step 1: Write the Skill

Create `skills/my-skill/SKILL.md` with generic instructions:

```markdown
# My Skill

You are an expert in [domain]...

## Responsibilities
1. [Task 1]
2. [Task 2]

## Workflow
When invoked:
1. [Step 1]
2. [Step 2]
```

**Important**: Keep the skill generic! Don't reference SpecKit-specific paths or commands.

### Step 2: Create the Adapter

Create `skills/my-skill/speckit-adapter.yaml`:

```yaml
name: my-skill
hooks:
  - phase: implement
    priority: 50
    context: SKILL.md
    instructions: |
      ## SpecKit Integration
      - Add framework-specific orchestration here
      - Reference SpecKit paths (.specify/memory/system-map.md, etc.)
```

### Step 3: Test

```bash
# Test the resolver
python3 scripts/resolve-skills.py implement

# Test in a real workflow
export SPECIFY_FEATURE=feat/999-test-skill
./scripts/bash/update-agent-context.sh claude implement
cat CLAUDE.md  # Verify skill was injected
```

## Multi-Phase Skills

A skill can hook into multiple phases:

```yaml
name: speckit-developer
hooks:
  - phase: tasks
    priority: 90
    context: SKILL.md
  - phase: implement
    priority: 100
    context: SKILL.md
```

This allows the same skill to influence multiple workflow stages.

## Context Funnel Strategy

Skills work with the **Context Funnel** pattern:

1. **System Map** (`.specify/memory/system-map.md`): Index of ALL documentation
2. **Plan Phase** (`speckit-architect`): Filters to "Relevant System Context"
3. **Task Phase** (`speckit-tech-lead`): Binds specific docs to tasks
4. **Implement Phase** (`speckit-developer`): Uses only task-relevant context

Each phase narrows the context, ensuring agents aren't overwhelmed.

## `.speckit.yaml` Configuration

Skills scanning can be customized via an optional `.speckit.yaml` file at the repository root:

```yaml
# SpecKit version (soft warning on major mismatch)
version: "2.0.0"

# Skills configuration
skills:
  # Override default scan directories
  scan_dirs:
    - skills/
    - .specify/skills/
    - .github/skills/
    - .claude/skills/
    - vendor/skills/     # Custom directory

# Memory configuration
memory:
  system_map: .specify/memory/system-map.md
  constitution: .specify/memory/constitution.md
```

**Zero-config compatible**: Without `.speckit.yaml`, the resolver uses default scan directories: `skills/`, `.specify/skills/`, `.github/skills/`, `.claude/skills/`.

See `templates/speckit-config-template.yaml` for the full configuration template.

## Best Practices

### Skill Design

- ✅ **DO**: Write skills as role-based prompts ("You are a...")
- ✅ **DO**: Define clear responsibilities and workflows
- ✅ **DO**: Make skills generic and portable
- ❌ **DON'T**: Reference SpecKit-specific file paths in `SKILL.md`
- ❌ **DON'T**: Assume phase context in the skill itself

### Adapter Configuration

- ✅ **DO**: Use descriptive skill names
- ✅ **DO**: Set priority to control load order
- ✅ **DO**: Map skills to appropriate lifecycle phases
- ❌ **DON'T**: Create circular dependencies between skills
- ❌ **DON'T**: Overload a single phase with too many skills

### Testing

- ✅ **DO**: Test skills in isolation with `resolve-skills.py`
- ✅ **DO**: Verify agent behavior in actual workflows
- ✅ **DO**: Check for context overflow (skill + plan + spec < token limit)
- ❌ **DON'T**: Deploy untested skills to production workflows

## Troubleshooting

### Skill Not Loading

1. **Check adapter syntax**: Validate YAML with `python3 -m yaml <file>`
2. **Check phase name**: Ensure phase matches command (plan/tasks/implement/converge)
3. **Check file paths**: Verify `context: SKILL.md` points to existing file
4. **Check script execution**: Run `resolve-skills.py <phase>` manually

### Skill Content Corrupted

1. **Check encoding**: Skills must be UTF-8 encoded
2. **Check frontmatter**: Remove YAML frontmatter from `SKILL.md` (use adapter instead)
3. **Check special characters**: Escape or remove characters that break Markdown

### Multiple Skills Conflicting

1. **Check priorities**: Higher priority skills load first
2. **Check instructions**: Ensure skills don't contradict each other
3. **Consider merging**: If two skills always run together, combine them

## Practical Example: mcp-builder in Feature 002

The `mcp-builder` skill was used during the MCP Helm Chart Deployment feature (`002-mcp-chart-deployment`) to demonstrate skill-first development:

**Skill Alignment** (from `plan.md`):

| Requirement | Matched Skill | Usage |
|-------------|---------------|-------|
| Image-based Deployment | mcp-builder | Leveraged existing Docker build patterns |
| NPM-based Deployment | mcp-builder | Utilized NPM publishing workflow |
| Chart Release Automation | mcp-builder | Extended release workflow following Docker release pattern |

**Key Integration Points**:

- `mcp/scripts/publish-chart.sh` follows the same pattern as `mcp/scripts/build-docker.sh` (from mcp-builder)
- Release workflow version synchronization uses `mcp/package.json` (per mcp-builder's NPM release pattern)
- Chart lint/template validation mirrors the "Build & Test" step in the mcp-builder workflow

This demonstrates the **Skill Alignment Strategy** in practice: when a skill exists for a task, it takes precedence over ad-hoc implementation approaches.

## Future Extensions

### Planned Features

1. **Conditional Loading**: Load skills based on tech stack (e.g., `python-developer` only for Python projects)
2. **Skill Dependencies**: Define prerequisite skills that must load together
3. **Skill Versioning**: Support multiple versions of the same skill
4. **Dynamic Discovery**: Auto-detect skills in `.specify/skills/` and `.github/skills/`

### Extensibility

The system is designed for extension:

- **Custom Phases**: Add new lifecycle phases beyond plan/tasks/implement/converge
- **External Skills**: Load skills from remote repositories
- **Skill Marketplaces**: Share skills across projects and teams
- **Agent-Specific Overrides**: Different skill bindings per AI agent type

---

**Last Updated**: 2026-02-13  
**Version**: 2.0.0  
**Maintainer**: SpecKit Core Team
