# Scripts Reference

Detailed documentation for all speckit-vibe scripts. All scripts use Python 3 standard library only.

---

## init_spec.py

Generate SPECIFICATION.md from template with validated user input and automatic directory isolation.

### Purpose

Creates a standardized SPECIFICATION.md file by rendering the template with user-provided data. Supports automatic directory isolation with sequential numbering for concurrent feature development.

**IMPORTANT**: The Agent must collect all information through conversation with the user BEFORE calling this script. This script does NOT handle user interaction.

### Usage

```bash
python3 scripts/init_spec.py [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--from-json FILE` | Load requirements from JSON file (recommended) |
| `--name NAME` | Feature name (required for quick mode) |
| `--overview TEXT` | Brief feature description (required for quick mode) |
| `--requirements TEXT` | User requirements description (required for quick mode) |
| `--business-value TEXT` | Business value (use \| to separate items) |
| `--target-users TEXT` | Target users (use \| to separate items) |
| `--constraints TEXT` | Constraints (use \| to separate items) |
| `--acceptance-criteria TEXT` | Acceptance criteria (use \| to separate items) |
| `--out-of-scope TEXT` | Out of scope items (use \| to separate items) |
| `--questions TEXT` | Questions/clarifications (use \| to separate items) |
| `--auto-dir` | **NEW**: Automatically create isolated work directory (specs/NNN-feature-name/) |
| `--work-dir DIR` | **NEW**: Use existing work directory (must exist) |
| `--specs-base DIR` | **NEW**: Base directory for specs (default: specs) |
| `--save-json` | **NEW**: Save requirements.json to work directory (automatic with --auto-dir) |
| `--output FILE` | Output file path (default: SPECIFICATION.md, ignored with --auto-dir/--work-dir) |
| `--force` | Overwrite output file if it exists |
| `--dry-run` | Print output to stdout without writing file |

### Directory Isolation Features

**Automatic Directory Creation** (`--auto-dir`):
- ✅ Creates isolated directory: `specs/001-feature-name/`, `specs/002-feature-name/`, etc.
- ✅ Sequential numbering prevents conflicts
- ✅ Generates slug from feature name (e.g., "OAuth2 Integration" → "oauth2-integration")
- ✅ Creates standard subdirectories: `sessions/`, `checklists/`, `copilot-logs/`
- ✅ Saves `requirements.json` for traceability
- ✅ Updates `.latest` symlink to newest feature
- ✅ **Race condition safe**: Handles concurrent directory creation

**Benefits**:
- Supports concurrent feature development (no file conflicts)
- Preserves original requirements data
- Works seamlessly with `vibe_workflow.py --spec-dir`
- Consistent directory structure across all features

### JSON Schema

For `--from-json` mode, use this structure:

```json
{
  "feature_name": "string (required)",
  "overview": "string (required)",
  "user_requirements": "string (required)",
  "business_value": ["string", ...],
  "target_users": ["string", ...],
  "constraints": ["string", ...],
  "acceptance_criteria": ["string", ...],
  "out_of_scope": ["string", ...],
  "questions": ["string", ...]
}
```

### Examples

**Example 1: Auto Directory (Recommended - Supports Concurrent Features)**

```bash
# 1. Create requirements.json with collected data
cat > /tmp/requirements.json << 'EOF'
{
  "feature_name": "OAuth2 Integration",
  "overview": "Add OAuth2 authentication support for third-party login providers",
  "user_requirements": "Users should be able to login using Google, GitHub, or Microsoft accounts instead of traditional username/password",
  "business_value": [
    "Reduce friction in user onboarding process",
    "Eliminate password management overhead for users",
    "Improve security with industry-standard OAuth2 flows"
  ],
  "target_users": [
    "End users who prefer social login",
    "Enterprise users with existing SSO"
  ],
  "constraints": [
    "Must support PKCE flow for enhanced security",
    "Must work with existing session management",
    "Must not break current local authentication"
  ],
  "acceptance_criteria": [
    "Users can login with Google OAuth2",
    "Users can login with GitHub OAuth2",
    "Users can login with Microsoft OAuth2",
    "Existing local auth still works",
    "Session management is maintained"
  ],
  "out_of_scope": [
    "SAML support",
    "Custom OAuth2 provider configuration",
    "Account linking between providers"
  ],
  "questions": []
}
EOF

# 2. Generate isolated directory and SPECIFICATION.md
python3 scripts/init_spec.py --from-json /tmp/requirements.json --auto-dir

# Output:
# ✓ Created work directory: specs/001-oauth2-integration/
# ✓ Saved: specs/001-oauth2-integration/requirements.json
# ✓ Generated: specs/001-oauth2-integration/SPECIFICATION.md
#
# Next step:
#   python3 scripts/vibe_workflow.py --auto --spec-dir specs/001-oauth2-integration
```

**Example 2: Quick Mode with Auto Directory**

```bash
python3 scripts/init_spec.py \
  --name "User Profile API" \
  --overview "REST API for user profile management" \
  --requirements "CRUD operations for user profiles" \
  --acceptance-criteria "GET profile works|POST profile works|PUT profile works|DELETE profile works" \
  --auto-dir
```

**Example 3: Use Existing Directory**

```bash
# If directory already exists (e.g., specs/001-oauth2/)
python3 scripts/init_spec.py \
  --from-json requirements.json \
  --work-dir specs/001-oauth2
```

**Example 4: Dry Run (Preview output)**

```bash
python3 scripts/init_spec.py \
  --from-json requirements.json \
  --dry-run
```

### Workflow Integration

**Recommended workflow with directory isolation:**

```bash
# Step 1: Generate isolated directory and spec
python3 scripts/init_spec.py --from-json /tmp/requirements.json --auto-dir

# Step 2: Run workflow in isolated directory
python3 scripts/vibe_workflow.py --auto --spec-dir specs/001-feature-name
```

### Directory Coordination with vibe_workflow.py

**How init_spec.py and vibe_workflow.py coordinate:**

1. **init_spec.py** creates the directory structure FIRST (when using `--auto-dir`)
2. **vibe_workflow.py** receives the directory path via `--spec-dir` parameter
3. **vibe_workflow.py** detects the directory exists and does NOT create a new one
4. All workflow stages work within the same isolated directory
5. All speckit.* agents inherit the working directory from the workflow

**Key Point**: When using `--spec-dir`, `vibe_workflow.py` will:
- ✅ Use the existing directory (no duplicate creation)
- ✅ Find SPECIFICATION.md in that directory
- ✅ Generate all outputs (spec.md, plan.md, tasks.md) in the same directory
- ✅ Pass the directory to all speckit.* agents

This ensures **perfect isolation** between concurrent features with **zero conflicts**.

### Error Handling

The script validates:
- ✅ Required fields are present (feature_name, overview, user_requirements)
- ✅ JSON is valid (if using --from-json)
- ✅ Template file exists
- ✅ Output file doesn't exist (unless --force is used)

Common errors:
- Missing required fields → Script exits with clear error message
- Invalid JSON → Script shows JSON parsing error
- File already exists → Use `--force` to overwrite

---

## vibe_workflow.py

Main workflow orchestrator that runs the complete speckit workflow.

### Usage

```bash
python3 scripts/vibe_workflow.py [OPTIONS] [REQUIREMENT]
```

### Options

| Option | Description |
|--------|-------------|
| `--interactive` | Start with Q&A phase (default for new requirements) |
| `--auto` | Run full autonomous workflow (AI answers own questions) |
| `--no-ask-user` | Prevent AI from asking user questions (use with --auto) |
| `--spec FILE` | Use existing SPECIFICATION.md |
| `--spec-dir DIR` | Use existing spec directory |
| `--stage STAGE` | Start from specific stage |
| `--resume` | Resume from last incomplete stage (uses state.json) |
| `--config FILE` | Use custom config file |
| `--log-level LEVEL` | Override log level (DEBUG\|INFO\|WARN\|ERROR) |
| `--dry-run` | Show what would be executed without running |

### Examples

```bash
# Full autonomous workflow with isolated directory
python3 scripts/vibe_workflow.py --auto --spec-dir specs/001-oauth2-integration

# Resume interrupted workflow
python3 scripts/vibe_workflow.py --resume

# Start from specific stage
python3 scripts/vibe_workflow.py --stage implement --spec-dir specs/001-oauth2

# Dry run to see execution plan
python3 scripts/vibe_workflow.py --dry-run --spec-dir specs/001-feature
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Config error |
| 4 | Stage failed |
| 5 | Interrupted |

---

## vibe_task.py

Execute individual tasks with vibe coding, supporting parallel execution.

### Usage

```bash
python3 scripts/vibe_task.py [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--task ID` | Execute specific task (e.g., T001) |
| `--phase N` | Execute all tasks in phase N |
| `--all` | Execute all tasks |
| `--parallel` | Enable parallel execution within phases |
| `--spec-dir DIR` | Spec directory path (in spec-vibes/) |
| `--dry-run` | Show command without executing |
| `--max-parallel N` | Override max parallel from config |

### Examples

```bash
# Single task
python3 scripts/vibe_task.py --task T005 --spec-dir spec-vibes/001-feature

# Phase with parallelism
python3 scripts/vibe_task.py --phase 3 --parallel --spec-dir spec-vibes/001-feature

# All tasks sequentially
python3 scripts/vibe_task.py --all --spec-dir spec-vibes/001-feature

# All tasks with parallel execution
python3 scripts/vibe_task.py --all --parallel --spec-dir spec-vibes/001-feature
```

### Task Format Recognition

The script parses tasks.md for task markers:

```markdown
- [ ] T001 [P] [US1] Create User model in src/models/user.py
      │     │    │
      │     │    └── User Story label
      │     └── Parallel marker (can run concurrently)
      └── Task ID
```

---

## config-manager.py

Manage `.speckit-vc.json` configuration file.

### Usage

```bash
python3 scripts/config-manager.py COMMAND [OPTIONS]
```

### Commands

| Command | Description |
|---------|-------------|
| `init` | Create default config file |
| `show` | Display current config |
| `set KEY VALUE` | Set config value |
| `get KEY` | Get config value |
| `validate` | Validate config file |
| `reset` | Reset to defaults |
| `adapters` | List available agent adapters |

### Examples

```bash
# Initialize default config
python3 scripts/config-manager.py init

# View current config
python3 scripts/config-manager.py show

# Set values
python3 scripts/config-manager.py set max_parallel 5
python3 scripts/config-manager.py set agent copilot
python3 scripts/config-manager.py set agent_config.copilot.model claude-sonnet-4.5

# Get values
python3 scripts/config-manager.py get agent
python3 scripts/config-manager.py get agent_config.copilot

# List available adapters
python3 scripts/config-manager.py adapters
python3 scripts/config-manager.py adapters --verbose

# Validate config
python3 scripts/config-manager.py validate
```

---

## state-tracker.py

Track workflow state for resume capability.

### Usage

```bash
python3 scripts/state-tracker.py COMMAND [OPTIONS]
```

### Commands

| Command | Description |
|---------|-------------|
| `status` | Show current workflow state |
| `checkpoint STAGE` | Mark stage as completed |
| `reset` | Reset workflow state |
| `resume` | Get next stage to execute |

### Examples

```bash
# Check current state
python3 scripts/state-tracker.py status --spec-dir spec-vibes/001-feature

# Mark stage completed
python3 scripts/state-tracker.py checkpoint clarify --spec-dir spec-vibes/001-feature

# Get next stage to run
python3 scripts/state-tracker.py resume --spec-dir spec-vibes/001-feature

# Reset workflow state
python3 scripts/state-tracker.py reset --spec-dir spec-vibes/001-feature
```

### State File Format

State is stored in `state.json`:

```json
{
  "spec_dir": "spec-vibes/001-feature",
  "current_stage": "plan",
  "completed_stages": ["specify", "clarify"],
  "failed_stages": [],
  "started_at": "2026-02-04T10:30:00Z",
  "last_updated": "2026-02-04T10:45:00Z"
}
```

---

## learning-collector.py

Collect and categorize learnings from sessions to update AGENTS.md.

### Usage

```bash
python3 scripts/learning-collector.py [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--session-log FILE` | Parse session log for learnings |
| `--category CAT` | Filter by category |
| `--update-agents` | Update AGENTS.md with learnings |
| `--dry-run` | Show changes without applying |
| `--list` | List pending learnings |

### Examples

```bash
# Collect learnings from a session
python3 scripts/learning-collector.py --session-log spec-vibes/001-feature/sessions/session-001.log

# Preview AGENTS.md updates
python3 scripts/learning-collector.py --update-agents --dry-run

# Apply learnings to AGENTS.md
python3 scripts/learning-collector.py --update-agents

# List pending learnings
python3 scripts/learning-collector.py --list

# Filter by category
python3 scripts/learning-collector.py --list --category code-patterns
```

### Learning Categories

| Category | Description | Example |
|----------|-------------|---------|
| `code-patterns` | Coding patterns discovered | Missing null check pattern |
| `tool-usage` | Tool usage issues | Incorrect git command sequence |
| `workflow-issues` | Workflow problems | Stage dependency missed |
| `model-limitations` | AI model limitations | Hallucinated API endpoint |

---

## Error Handling

All scripts follow consistent error handling:

| Error Code | Name | Cause | Resolution |
|------------|------|-------|------------|
| `SPECKIT_NOT_FOUND` | Agent Missing | speckit agents not installed | Install speckit to .github/agents/ |
| `CONFIG_INVALID` | Config Error | Invalid .speckit-vc.json | Run `config-manager.py validate` |
| `STAGE_FAILED` | Stage Failure | Workflow stage failed | Check session log, retry with `--stage` |
| `TASK_TIMEOUT` | Timeout | Task exceeded time limit | Increase timeout or split task |
| `PARALLEL_CONFLICT` | Conflict | Concurrent file access | Reduce `max_parallel` or mark sequential |

### Skill Self-Error Logging

Script errors are logged separately to `skill-errors.log`:

```bash
# View skill errors for a session
cat spec-vibes/001-user-auth/skill-errors.log
```

This separates skill bugs from workflow/implementation issues.
