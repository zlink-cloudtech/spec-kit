# AGENTS.md

## About Spec Kit and Specify

**GitHub Spec Kit** is a comprehensive toolkit for implementing Spec-Driven Development (SDD) - a methodology that emphasizes creating clear specifications before implementation. The toolkit includes templates, scripts, and workflows that guide development teams through a structured approach to building software.

**Specify CLI** is the command-line interface that bootstraps projects with the Spec Kit framework. It sets up the necessary directory structures, templates, and AI agent integrations to support the Spec-Driven Development workflow.

The toolkit supports multiple AI coding assistants, allowing teams to use their preferred tools while maintaining consistent project structure and development practices.

---

## Project Architecture

### Directory Structure

```text
spec-kit/
├── src/specify_cli/       # Specify CLI source (Python/Typer)
│   └── __init__.py        # Main CLI entry point — AGENT_CONFIG, init(), check(), version()
├── scripts/
│   ├── bash/              # Bash scripts for feature creation, context update, common utilities
│   ├── powershell/        # PowerShell equivalents of all bash scripts
│   └── resolve-skills.py  # Phase-based skill resolver (reads .speckit.yaml)
├── templates/
│   ├── commands/          # Slash command templates (specify, clarify, plan, tasks, implement, converge, etc.)
│   ├── instructions/      # Agent instruction templates
│   ├── spec-template.md, plan-template.md, tasks-template.md, system-map-template.md, etc.
│   └── speckit-config-template.yaml
├── skills/                # AI agent skill personas
│   ├── speckit-architect/     # Plan phase — high-level design, ADRs, gap analysis
│   ├── speckit-developer/     # Implement/tasks phase — TDD, clean code
│   ├── speckit-librarian/     # Converge phase — documentation, system map
│   ├── speckit-tech-lead/     # Tasks phase — task planning, dependency management
│   ├── speckit-vibe/          # Autonomous vibe coding workflow
│   ├── release-server-developer/  # Release server management
│   ├── skill-creator/        # Meta-skill for creating new skills
│   ├── readme-creator/       # README generation
│   ├── mcp-builder/          # MCP server creation
│   └── speckit-*/             # Other speckit-prefixed skills
├── docs/                  # Project documentation
├── specs/                 # Feature specification directories (###-feature-name/)
├── tests/                 # Test suite
├── release-server/        # Release server component (Docker-based)
├── mcp/                   # MCP Helm chart deployment
├── .devcontainer/         # Devcontainer configuration
└── pyproject.toml         # Project metadata (version, dependencies)
```

### 6-Phase Lifecycle

The Spec-Driven Development lifecycle consists of 6 sequential phases:

```text
Specify → Clarify → Plan → Task → Implement → Converge
```

| Phase | Command | Skill Persona | Description |
|-------|---------|---------------|-------------|
| **Specify** | `/speckit.specify` | — | Create feature specification from natural language |
| **Clarify** | `/speckit.clarify` | — | Ask targeted questions to de-risk ambiguities (optional) |
| **Plan** | `/speckit.plan` | speckit-architect | Design architecture, ADRs, data models, contracts |
| **Task** | `/speckit.tasks` | speckit-tech-lead, speckit-developer | Generate dependency-ordered tasks with CONVERGENCE_BOUNDARY |
| **Implement** | `/speckit.implement` | speckit-developer | Execute Phases 1 through N-1 (hard stop at CONVERGENCE_BOUNDARY) |
| **Converge** | `/speckit.converge` | speckit-librarian | Phase N — update docs, ADRs, system map, close gaps |

**Additional Commands:**

| Command | Purpose |
|---------|---------|
| `/speckit.constitution` | Establish project principles and governance |
| `/speckit.analyze` | Cross-artifact consistency check (after tasks, before implement) |
| `/speckit.checklist` | Generate quality checklists for requirements validation |
| `/speckit.taskstoissues` | Convert tasks into GitHub issues for team collaboration |

### Branch Naming Convention

Branches use a **`type/###-name`** format with 6 supported types:

```text
feat/001-user-auth        # New feature
bug/002-login-crash       # Bug fix
hotfix/003-db-fix         # Emergency production fix
refactor/004-auth-module  # Code restructuring
docs/005-api-guide        # Documentation
chore/006-deps-update     # Build/tooling/dependencies
```

**Key rules:**

- Default type is `feat`; set via `--type` (bash) or `-Type` (PowerShell)
- **Global sequential numbering** — all types share one counter (001, 002, 003...)
- **Specs directory stays flat** — `feat/001-user-auth` maps to `specs/001-user-auth/`
- **`strip_branch_type()` / `Get-BranchWithoutType`** — helper functions strip the type prefix for specs mapping
- **Validation regex**: `^(feat|bug|hotfix|refactor|docs|chore)/[0-9]{3}-`
- **`SPECIFY_FEATURE`** env var stores the full branch name including type prefix (e.g., `feat/001-user-auth`)
- JSON output includes `BRANCH_TYPE` field

### Skill Architecture

Skills use the **Adapter Pattern** — each skill has:

- **`SKILL.md`**: Portable persona definition (no SpecKit-specific paths)
- **`speckit-adapter.yaml`**: SpecKit integration sidecar with phase hooks

```yaml
# Example: speckit-adapter.yaml
name: speckit-architect
hooks:
  - phase: plan
    priority: 100
    context: SKILL.md
    instructions: |
      ## SpecKit Integration
      - Read memory/system-map.md to identify touched components
      - Add Documentation State Matrix entries to plan.md
```

**Skill Resolution**: `scripts/python/resolve-skills.py` discovers skills via `.speckit.yaml` configuration, matches phase hooks, sorts by priority, and injects content into LLM prompts.

### Configuration (`.speckit.yaml`)

Optional project-level configuration:

```yaml
version: "2.0.0"
skills:
  scan_dirs:
    - skills/
    - .specify/skills/
    - .github/skills/
    - .claude/skills/
memory:
  system_map: .specify/memory/system-map.md
  constitution: .specify/memory/constitution.md
```

### CONVERGENCE_BOUNDARY

Tasks are split into two groups by a `<!-- CONVERGENCE_BOUNDARY -->` marker in `tasks.md`:

- **Phases 1 through N-1**: Implementation tasks executed by `/speckit.implement`
- **Phase N**: Documentation convergence tasks executed by `/speckit.converge`

`/speckit.implement` enforces a **hard stop** at the boundary marker. Phase N tasks can only run via `/speckit.converge`.

---

## General practices

- Any changes to `__init__.py` for the Specify CLI require a version rev in `pyproject.toml` and addition of entries to `CHANGELOG.md`.
- Both bash (`scripts/bash/`) and PowerShell (`scripts/powershell/`) scripts must be kept in sync — every feature must be implemented in both.
- Branch names must follow the `type/###-name` format (see Branch Naming Convention above).
- Spec directories use the flat `###-name` format (without type prefix) under `specs/`.
- When modifying slash command templates in `templates/commands/`, ensure examples and workflow descriptions match the current script parameters.

## Adding New Agent Support

This section explains how to add support for new AI agents/assistants to the Specify CLI. Use this guide as a reference when integrating new AI tools into the Spec-Driven Development workflow.

### Overview

Specify supports multiple AI agents by generating agent-specific command files and directory structures when initializing projects. Each agent has its own conventions for:

- **Command file formats** (Markdown, TOML, etc.)
- **Directory structures** (`.claude/commands/`, `.windsurf/workflows/`, etc.)
- **Command invocation patterns** (slash commands, CLI tools, etc.)
- **Argument passing conventions** (`$ARGUMENTS`, `{{args}}`, etc.)

### Current Supported Agents

| Agent                      | Directory              | Format   | CLI Tool        | Instruction Directory   | Skills Directory        | Description                 |
| -------------------------- | ---------------------- | -------- | --------------- | ----------------------- | ----------------------- | --------------------------- |
| **Claude Code**            | `.claude/commands/`    | Markdown | `claude`        | N/A                     | `.claude/skills/`       | Anthropic's Claude Code CLI |
| **Gemini CLI**             | `.gemini/commands/`    | TOML     | `gemini`        | N/A                     | `.specify/skills/`      | Google's Gemini CLI         |
| **GitHub Copilot**         | `.github/agents/`      | Markdown | N/A (IDE-based) | `.github/instructions/` | `.github/skills/`       | GitHub Copilot in VS Code   |
| **Cursor**                 | `.cursor/commands/`    | Markdown | `cursor-agent`  | N/A                     | `.specify/skills/`      | Cursor CLI                  |
| **Qwen Code**              | `.qwen/commands/`      | TOML     | `qwen`          | N/A                     | `.specify/skills/`      | Alibaba's Qwen Code CLI     |
| **opencode**               | `.opencode/command/`   | Markdown | `opencode`      | N/A                     | `.specify/skills/`      | opencode CLI                |
| **Codex CLI**              | `.codex/prompts/`      | Markdown | `codex`         | N/A                     | `.specify/skills/`      | Codex CLI                   |
| **Windsurf**               | `.windsurf/workflows/` | Markdown | N/A (IDE-based) | N/A                     | `.specify/skills/`      | Windsurf IDE workflows      |
| **Kilo Code**              | `.kilocode/workflows/` | Markdown | N/A (IDE-based) | N/A                     | `.specify/skills/`      | Kilo Code IDE               |
| **Auggie CLI**             | `.augment/commands/`   | Markdown | `auggie`        | N/A                     | `.specify/skills/`      | Auggie CLI                  |
| **Roo Code**               | `.roo/commands/`       | Markdown | N/A (IDE-based) | N/A                     | `.roo/skills/`          | Roo Code IDE                |
| **CodeBuddy CLI**          | `.codebuddy/commands/` | Markdown | `codebuddy`     | N/A                     | `.specify/skills/`      | CodeBuddy CLI               |
| **Qoder CLI**              | `.qoder/commands/`     | Markdown | `qoder`         | N/A                     | `.specify/skills/`      | Qoder CLI                   |
| **Amazon Q Developer CLI** | `.amazonq/prompts/`    | Markdown | `q`             | N/A                     | `.specify/skills/`      | Amazon Q Developer CLI      |
| **Amp**                    | `.agents/commands/`    | Markdown | `amp`           | N/A                     | `.specify/skills/`      | Amp CLI                     |
| **SHAI**                   | `.shai/commands/`      | Markdown | `shai`          | N/A                     | `.specify/skills/`      | SHAI CLI                    |
| **IBM Bob**                | `.bob/commands/`       | Markdown | N/A (IDE-based) | N/A                     | `.specify/skills/`      | IBM Bob IDE                 |

### Step-by-Step Integration Guide

Follow these steps to add a new agent (using a hypothetical new agent as an example):

#### 1. Add to AGENT_CONFIG

**IMPORTANT**: Use the actual CLI tool name as the key, not a shortened version.

Add the new agent to the `AGENT_CONFIG` dictionary in `src/specify_cli/__init__.py`. This is the **single source of truth** for all agent metadata:

```python
AGENT_CONFIG = {
    # ... existing agents ...
    "new-agent-cli": {  # Use the ACTUAL CLI tool name (what users type in terminal)
        "name": "New Agent Display Name",
        "folder": ".newagent/",  # Directory for agent files
        "install_url": "https://example.com/install",  # URL for installation docs (or None if IDE-based)
        "requires_cli": True,  # True if CLI tool required, False for IDE-based agents
    },
}
```

**Key Design Principle**: The dictionary key should match the actual executable name that users install. For example:

- ✅ Use `"cursor-agent"` because the CLI tool is literally called `cursor-agent`
- ❌ Don't use `"cursor"` as a shortcut if the tool is `cursor-agent`

This eliminates the need for special-case mappings throughout the codebase.

**Field Explanations**:

- `name`: Human-readable display name shown to users
- `folder`: Directory where agent-specific files are stored (relative to project root)
- `install_url`: Installation documentation URL (set to `None` for IDE-based agents)
- `requires_cli`: Whether the agent requires a CLI tool check during initialization
- `skills`: (Optional) Configuration for skills integration (currently only for Copilot)

#### 2. Update CLI Help Text

Update the `--ai` parameter help text in the `init()` command to include the new agent:

```python
ai_assistant: str = typer.Option(None, "--ai", help="AI assistant to use: claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, new-agent-cli, or q"),
```

Also update any function docstrings, examples, and error messages that list available agents.

#### 3. Update README Documentation

Update the **Supported AI Agents** section in `README.md` to include the new agent:

- Add the new agent to the table with appropriate support level (Full/Partial)
- Include the agent's official website link
- Add any relevant notes about the agent's implementation
- Ensure the table formatting remains aligned and consistent

#### 4. Update Release Package Script

Modify `.github/workflows/scripts/create-release-packages.sh`:

##### Add to ALL_AGENTS array

```bash
ALL_AGENTS=(claude gemini copilot cursor-agent qwen opencode windsurf q)
```

##### Add case statement for directory structure

```bash
case $agent in
  # ... existing cases ...
  windsurf)
    mkdir -p "$base_dir/.windsurf/workflows"
    generate_commands windsurf md "\$ARGUMENTS" "$base_dir/.windsurf/workflows" "$script" ;;
esac
```

#### 5. Update GitHub Release Script

Modify `.github/workflows/scripts/create-github-release.sh` to include the new agent's packages:

```bash
gh release create "$VERSION" \
  # ... existing packages ...
  .genreleases/spec-kit-template-windsurf-sh-"$VERSION".zip \
  .genreleases/spec-kit-template-windsurf-ps-"$VERSION".zip \
  # Add new agent packages here
```

#### 6. Update Agent Context Scripts

##### Bash script (`scripts/bash/update-agent-context.sh`)

Add file variable:

```bash
WINDSURF_FILE="$REPO_ROOT/.windsurf/rules/specify-rules.md"
```

Add to case statement:

```bash
case "$AGENT_TYPE" in
  # ... existing cases ...
  windsurf) update_agent_file "$WINDSURF_FILE" "Windsurf" ;;
  "")
    # ... existing checks ...
    [ -f "$WINDSURF_FILE" ] && update_agent_file "$WINDSURF_FILE" "Windsurf";
    # Update default creation condition
    ;;
esac
```

##### PowerShell script (`scripts/powershell/update-agent-context.ps1`)

Add file variable:

```powershell
$windsurfFile = Join-Path $repoRoot '.windsurf/rules/specify-rules.md'
```

Add to switch statement:

```powershell
switch ($AgentType) {
    # ... existing cases ...
    'windsurf' { Update-AgentFile $windsurfFile 'Windsurf' }
    '' {
        foreach ($pair in @(
            # ... existing pairs ...
            @{file=$windsurfFile; name='Windsurf'}
        )) {
            if (Test-Path $pair.file) { Update-AgentFile $pair.file $pair.name }
        }
        # Update default creation condition
    }
}
```

#### 7. Update CLI Tool Checks (if applicable)

CLI tool checks are handled automatically based on the `requires_cli` field in AGENT_CONFIG. The `check()` command loops through all agents and calls `check_tool(agent_key, tracker=tracker)` for those with `requires_cli: True`. IDE-based agents (`requires_cli: False`) are skipped automatically.

**No additional code changes needed** — just ensure `requires_cli` is set correctly in Step 1.

#### 8. Update Devcontainer Files (Optional)

For agents that have VS Code extensions or require CLI installation, update the devcontainer configuration files:

##### VS Code Extension-based Agents

For agents available as VS Code extensions, add them to `.devcontainer/devcontainer.json`:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        // ... existing extensions ...
        "[New Agent Extension ID]"
      ]
    }
  }
}
```

##### CLI-based Agents

For agents that require CLI tools, add installation commands to `.devcontainer/post-create.sh`:

```bash
#!/bin/bash

# Existing installations...

echo -e "\n🤖 Installing [New Agent Name] CLI..."
# run_command "npm install -g [agent-cli-package]@latest"
echo "✅ Done"
```

## Adding New Skills for Agents

Skills are specialized capabilities that provide AI agents with specific workflows, instructions, and strategies for complex tasks.

### Skill-First Development Policy

In the Spec-Driven Development (SDD) workflow, skills are considered the authoritative source of knowledge and capability.

1. **Alignment**: During Specification and Planning, requirements must be mapped to available skills.
2. **Priority**: If a skill exists for a task, it must be used instead of ad-hoc implementation.
3. **Authority**: Skill instructions override general training data or external documentation.

### Development Process

1. **Bootstrap with Skill Creator**

    Use the `skill-creator` skill to generate the initial structure. This ensures consistency and adherence to best practices.

2. **Create Skill Directory**

    Create a new directory in the `skills/` folder.

    - **Naming Convention**: Use **kebab-case** (all lowercase, hyphen-separated).
    - Example: `skills/my-new-skill/`

3. **Implement Skill Logic**
    Follow the specifications defined in the `skill-creator` skill. A standard skill typically includes:

    - `SKILL.md`: The core definition and instructions for the agent.
    - `scripts/`: Python or shell scripts that the agent can execute.
    - `reference/`: Contextual documentation.

4. **Verify Packaging**

    Ensure the new skill is being packaged correctly for your target agent. The `create-release-packages.sh` script automatically handles skill distribution:

    - **GitHub Copilot**: Skills are installed to `.github/skills/`
    - **Claude Code**: Skills are installed to `.claude/skills/`
    - **Other Agents**: Skills are installed to `.specify/skills/` (default behavior)

    No additional configuration in `AGENT_CONFIG` is required for basic file distribution. If your agent requires specific instruction injection, you may need to update the instructions template manually.

## Testing New Agent Integration

1. **Build test**: Run package creation script locally
2. **CLI test**: Test `specify init --ai <agent>` command
3. **File generation**: Verify correct directory structure and files
4. **Command validation**: Ensure generated commands work with the agent
5. **Context update**: Test agent context update scripts
6. **Branch naming**: Verify `create-new-feature.sh --type <type>` generates correct `type/###-name` branches
7. **Skill resolution**: Test `resolve-skills.py` discovers and injects skills for all lifecycle phases

## Common Pitfalls

1. **Using shorthand keys instead of actual CLI tool names**: Always use the actual executable name as the AGENT_CONFIG key (e.g., `"cursor-agent"` not `"cursor"`). The `check_tool()` function uses `shutil.which(tool)` to find executables — if the key doesn't match the real tool name, you'll need special-case mappings everywhere.
2. **Forgetting update scripts**: Both bash and PowerShell scripts must be updated when adding new agents.
3. **Incorrect `requires_cli` value**: Set to `True` only for agents that actually have CLI tools to check; set to `False` for IDE-based agents.
4. **Wrong argument format**: Use correct placeholder format for each agent type (`$ARGUMENTS` for Markdown, `{{args}}` for TOML).
5. **Directory naming**: Follow agent-specific conventions exactly (check existing agents in the release script's `case` statement for patterns).
6. **Help text inconsistency**: Update all user-facing text consistently (help strings, docstrings, README, error messages).
7. **Branch type/specs mismatch**: Branch names include the type prefix (`feat/001-name`) but specs directories do NOT (`specs/001-name/`). Always use `strip_branch_type()` / `Get-BranchWithoutType` when mapping from branch to specs directory.
8. **Forgetting CONVERGENCE_BOUNDARY**: When modifying task templates, ensure the `<!-- CONVERGENCE_BOUNDARY -->` marker is present to separate implementation and convergence phases.

## Important Design Decisions

### Using Actual CLI Tool Names as Keys

**CRITICAL**: When adding a new agent to AGENT_CONFIG, always use the **actual executable name** as the dictionary key, not a shortened or convenient version.

**Why this matters:**

- The `check_tool()` function uses `shutil.which(tool)` to find executables in the system PATH
- If the key doesn't match the actual CLI tool name, you'll need special-case mappings throughout the codebase
- This creates unnecessary complexity and maintenance burden

**Example — The Cursor Lesson:**

❌ **Wrong approach** (requires special-case mapping):

```python
AGENT_CONFIG = {
    "cursor": {  # Shorthand that doesn't match the actual tool
        "name": "Cursor",
        # ...
    }
}

# Then you need special cases everywhere:
cli_tool = agent_key
if agent_key == "cursor":
    cli_tool = "cursor-agent"  # Map to the real tool name
```

✅ **Correct approach** (no mapping needed):

```python
AGENT_CONFIG = {
    "cursor-agent": {  # Matches the actual executable name
        "name": "Cursor",
        # ...
    }
}

# No special cases needed - just use agent_key directly!
```

**Benefits of this approach:**

- Eliminates special-case logic scattered throughout the codebase
- Makes the code more maintainable and easier to understand
- Reduces the chance of bugs when adding new agents
- Tool checking "just works" without additional mappings

#### 7. Update Devcontainer files (Optional)

For agents that have VS Code extensions or require CLI installation, update the devcontainer configuration files:

##### VS Code Extension-based Agents

For agents available as VS Code extensions, add them to `.devcontainer/devcontainer.json`:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        // ... existing extensions ...
        // [New Agent Name]
        "[New Agent Extension ID]"
      ]
    }
  }
}
```

##### CLI-based Agents

For agents that require CLI tools, add installation commands to `.devcontainer/post-create.sh`:

```bash
#!/bin/bash

# Existing installations...

echo -e "\n🤖 Installing [New Agent Name] CLI..."
# run_command "npm install -g [agent-cli-package]@latest" # Example for node-based CLI
# or other installation instructions (must be non-interactive and compatible with Linux Debian "Trixie" or later)...
echo "✅ Done"

```

**Quick Tips:**

- **Extension-based agents**: Add to the `extensions` array in `devcontainer.json`
- **CLI-based agents**: Add installation scripts to `post-create.sh`
- **Hybrid agents**: May require both extension and CLI installation
- **Test thoroughly**: Ensure installations work in the devcontainer environment

## Agent Categories

### CLI-Based Agents

Require a command-line tool to be installed:

- **Claude Code**: `claude` CLI
- **Gemini CLI**: `gemini` CLI
- **Cursor**: `cursor-agent` CLI
- **Qwen Code**: `qwen` CLI
- **opencode**: `opencode` CLI
- **Amazon Q Developer CLI**: `q` CLI
- **CodeBuddy CLI**: `codebuddy` CLI
- **Qoder CLI**: `qoder` CLI
- **Amp**: `amp` CLI
- **SHAI**: `shai` CLI

### IDE-Based Agents

Work within integrated development environments:

- **GitHub Copilot**: Built into VS Code/compatible editors
- **Windsurf**: Built into Windsurf IDE
- **IBM Bob**: Built into IBM Bob IDE

## Command File Formats

### Markdown Format

Used by: Claude, Cursor, opencode, Windsurf, Amazon Q Developer, Amp, SHAI, IBM Bob

**Standard format:**

```markdown
---
description: "Command description"
---

Command content with {SCRIPT} and $ARGUMENTS placeholders.
```

**GitHub Copilot Chat Mode format:**

```markdown
---
description: "Command description"
mode: speckit.command-name
---

Command content with {SCRIPT} and $ARGUMENTS placeholders.
```

### TOML Format

Used by: Gemini, Qwen

```toml
description = "Command description"

prompt = """
Command content with {SCRIPT} and {{args}} placeholders.
"""
```

## Instruction File Formats

### copilot-instructions Format

Used by: GitHub Copilot

```markdown
---
name: Instruction Name
description: Description of the instruction
applyTo: "**"
---

Instruction content...
```

### markdown Format

Used by: Other agents (if applicable)

```markdown
---
description: Description of the instruction
---

Instruction content...
```

## Directory Conventions

- **CLI agents**: Usually `.<agent-name>/commands/`
- **IDE agents**: Follow IDE-specific patterns:
  - Copilot: `.github/agents/` (commands) and `.github/instructions/` (instructions)
  - Cursor: `.cursor/commands/`
  - Windsurf: `.windsurf/workflows/`

## Argument Patterns

Different agents use different argument placeholders:

- **Markdown/prompt-based**: `$ARGUMENTS`
- **TOML-based**: `{{args}}`
- **Script placeholders**: `{SCRIPT}` (replaced with actual script path)
- **Agent placeholders**: `__AGENT__` (replaced with agent name)

## Testing New Agent Integration (Summary)

1. **Build test**: Run package creation script locally
2. **CLI test**: Test `specify init --ai <agent>` command
3. **File generation**: Verify correct directory structure and files
4. **Command validation**: Ensure generated commands work with the agent
5. **Context update**: Test agent context update scripts

## Common Pitfalls (Summary)

1. **Using shorthand keys instead of actual CLI tool names**: Always use the actual executable name as the AGENT_CONFIG key (e.g., `"cursor-agent"` not `"cursor"`). This prevents the need for special-case mappings throughout the codebase.
2. **Forgetting update scripts**: Both bash and PowerShell scripts must be updated when adding new agents.
3. **Incorrect `requires_cli` value**: Set to `True` only for agents that actually have CLI tools to check; set to `False` for IDE-based agents.
4. **Wrong argument format**: Use correct placeholder format for each agent type (`$ARGUMENTS` for Markdown, `{{args}}` for TOML).
5. **Directory naming**: Follow agent-specific conventions exactly (check existing agents for patterns).
6. **Help text inconsistency**: Update all user-facing text consistently (help strings, docstrings, README, error messages).

## Future Considerations

When adding new agents:

- Consider the agent's native command/workflow patterns
- Ensure compatibility with the Spec-Driven Development process
- Document any special requirements or limitations
- Update this guide with lessons learned
- Verify the actual CLI tool name before adding to AGENT_CONFIG

---

*This documentation should be updated whenever new agents are added to maintain accuracy and completeness.*
