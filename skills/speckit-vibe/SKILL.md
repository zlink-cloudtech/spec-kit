---
name: speckit-vibe
description: >-
  Autonomous vibe coding workflow for spec-driven development.
  
  **USING speckit-vibe** - Trigger when:
  (1) "vibe coding", "implement feature automatically", "autonomous development"
  (2) "run speckit workflow", "specify → clarify → plan → tasks"
  (3) "resume workflow", "continue vibe coding"
  (4) "execute task", "run task T001"
  (5) "configure speckit", "set max_parallel"
  
  **DEVELOPING speckit-vibe** - Trigger when:
  (6) "create new adapter", "extend speckit-vibe", "add agent support"
  (7) "modify vibe scripts", "debug speckit-vibe", "fix workflow bug"
---

# Speckit Vibe Coding

Autonomous vibe coding skill that transforms natural language requirements into working code through the speckit workflow, with AI-driven decision making and session isolation.

---

## Scenarios

### Scenario 1: Start New Feature (Most Common)

**Triggers**: "vibe code this", "implement feature", "build with vibe coding"

> **CRITICAL**: When the user wants to start a new feature, YOU (the Agent) must directly interact with the user to understand their requirements. Do NOT run `--interactive` mode in a script.

**Step 1: Gather Requirements (Agent-Driven Q&A)**

> **YOU MUST** collect all information through conversation before calling init_spec.py. The script does NOT handle user interaction.

Ask the user clarifying questions directly in the chat. Cover these areas:

1. **Core functionality**: What exactly should the feature do?
2. **User roles**: Who will use this? Authentication/authorization needs?
3. **Data models**: What data entities are involved? Relationships?
4. **External integrations**: APIs, services, databases?
5. **Performance requirements**: Scale, latency, throughput expectations?
6. **Error handling**: How should errors be surfaced?
7. **Technology constraints**: Specific languages, frameworks, patterns to follow?
8. **Acceptance criteria**: How will we know this is done correctly?
9. **Scope boundaries**: What is explicitly NOT included?

**Data Collection Template** - Map conversation to JSON structure:
- `feature_name`: Short, descriptive name
- `overview`: 1-2 sentence description  
- `user_requirements`: Natural language description of what user wants
- `business_value`: Why is this needed? (array of strings)
- `target_users`: Who will use this? (array of strings)
- `constraints`: Technical or business limitations (array of strings)
- `acceptance_criteria`: What must be true for completion? (array of strings)
- `out_of_scope`: What is explicitly NOT included? (array of strings)
- `questions`: Unresolved clarifications (array of strings)

**Step 2: Generate SPECIFICATION.md with Isolated Directory**

After gathering sufficient information, use the `init_spec.py` script to generate a validated SPECIFICATION.md in an isolated work directory.

> **⭐ RECOMMENDED**: Use `--auto-dir` for automatic directory isolation. This enables concurrent feature development without conflicts.

**Method A: Auto Directory (Recommended - Supports Concurrent Features)**

Create isolated work directory automatically with sequential numbering (001, 002, 003...):

1. Save collected information to a temporary JSON file:
   ```bash
   cat > /tmp/requirements.json << 'EOF'
   {
     "feature_name": "OAuth2 Integration",
     "overview": "Add OAuth2 authentication support for third-party login",
     "user_requirements": "Users should be able to login using Google, GitHub, or Microsoft accounts",
     "business_value": [
       "Reduce friction in user onboarding",
       "Eliminate password management overhead"
     ],
     "target_users": ["End users who prefer social login"],
     "constraints": ["Must support PKCE flow", "Must work with existing sessions"],
     "acceptance_criteria": [
       "Users can login with Google OAuth2",
       "Users can login with GitHub OAuth2"
     ],
     "out_of_scope": ["SAML support"],
     "questions": []
   }
   EOF
   ```
   
   💡 **See**: `assets/templates/requirements.example.json` for a complete example

2. Generate isolated work directory and SPECIFICATION.md:
   ```bash
   python3 scripts/init_spec.py --from-json /tmp/requirements.json --auto-dir
   ```
   
   Output:
   ```
   ✓ Created work directory: specs/001-oauth2-integration/
   ✓ Saved: specs/001-oauth2-integration/requirements.json
   ✓ Generated: specs/001-oauth2-integration/SPECIFICATION.md
   
   Next step:
     python3 scripts/vibe_workflow.py --auto --spec-dir specs/001-oauth2-integration
   ```

**Benefits of `--auto-dir`**:
- ✅ Automatic directory isolation with sequential numbering (001, 002, 003...)
- ✅ Supports concurrent feature development (no file conflicts)
- ✅ Preserves `requirements.json` for traceability
- ✅ Creates standard directory structure (sessions/, checklists/, copilot-logs/)
- ✅ Works seamlessly with `vibe_workflow.py --spec-dir`
- ✅ Maintains `.latest` symlink to most recent feature

**Method B: Quick Mode with Auto Directory**

For simple specs, use command-line arguments with `--auto-dir`:

```bash
python3 scripts/init_spec.py \
  --name "OAuth2 Integration" \
  --overview "Add OAuth2 authentication support" \
  --requirements "Users can login via Google, GitHub, Microsoft" \
  --acceptance-criteria "Google login works|GitHub login works|Auth is secure" \
  --auto-dir
```

**Validation**: The script will:
- ✅ Validate required fields (feature_name, overview, user_requirements)
- ✅ Apply consistent template formatting
- ✅ Prevent overwriting existing files (use --force if needed)
- ✅ Create isolated directory structure with `--auto-dir`
- ✅ Handle concurrent directory creation safely (race condition protection)

**Why use the script instead of creating the file manually?**
- Ensures consistent format matching the template
- Validates required fields are present
- Automatic directory isolation prevents conflicts
- Reduces token usage (template not loaded to context)
- Provides clear error messages for missing data

**Step 3: Run Autonomous Workflow**

Once the work directory is created, execute the full workflow non-interactively:

```bash
# Use --spec-dir to point to the isolated directory
python3 scripts/vibe_workflow.py --auto --spec-dir specs/001-oauth2-integration
```

> **Note**: When using `--spec-dir`, `vibe_workflow.py` uses the existing directory and does NOT create a new one. All workflow stages work within this isolated directory.

---

### Scenario 2: Run Full Autonomous Workflow

**Triggers**: "run speckit workflow", "execute full workflow on spec"

```bash
python3 scripts/vibe_workflow.py --auto --spec-dir specs/001-feature-name
```

Runs all stages: specify → clarify → plan → tasks → checklist → analyze → implement

---

### Scenario 3: Resume Interrupted Workflow

**Triggers**: "resume workflow", "continue from where we left off"

```bash
python3 scripts/vibe_workflow.py --resume
```

Uses `state.json` to continue from the last incomplete stage.

---

### Scenario 4: Execute Specific Tasks

**Triggers**: "run task T005", "execute phase 3 tasks"

```bash
# Single task
python3 scripts/vibe_task.py --task T001 --spec-dir spec-vibes/001-user-auth

# All tasks in a phase
python3 scripts/vibe_task.py --phase 3 --parallel --spec-dir spec-vibes/001-feature
```

---

### Scenario 5: Configure Settings

**Triggers**: "configure speckit", "set max_parallel", "change agent"

```bash
python3 scripts/config-manager.py init              # Create default config
python3 scripts/config-manager.py set max_parallel 5
python3 scripts/config-manager.py adapters          # List available adapters
```

---

### Scenario 6: Create New Agent Adapter (Development)

**Triggers**: "create new adapter", "add support for Claude CLI", "extend speckit-vibe"

→ **Read**: [🔧 Adapter Development Guide](references/adapter-guide.md)

Follow the adapter pattern to add support for new AI agents (Claude CLI, Aider, etc.).

---

### Scenario 7: Modify or Debug Scripts (Development)

**Triggers**: "fix vibe_workflow.py", "debug speckit-vibe", "modify task execution"

→ **Read**: [📜 Scripts Reference](references/scripts-reference.md)
→ **Read**: [🔧 Development Guide](references/development-guide.md)

---

## Workflow Overview

### Directory Isolation & Concurrent Features

```
┌──────────────────────────────────────────────────────────────────────┐
│                   DIRECTORY ISOLATION ARCHITECTURE                    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Project Root                                                         │
│  ├── specs/                    ← All features in isolated dirs       │
│  │   ├── 001-oauth2/           ← Feature 1 (can run concurrently)    │
│  │   │   ├── requirements.json                                       │
│  │   │   ├── SPECIFICATION.md                                        │
│  │   │   ├── spec.md                                                 │
│  │   │   ├── plan.md                                                 │
│  │   │   ├── tasks.md                                                │
│  │   │   ├── sessions/         ← Agent session logs                  │
│  │   │   ├── checklists/       ← Quality checklists                  │
│  │   │   └── copilot-logs/     ← Debug logs                          │
│  │   ├── 002-user-profile/     ← Feature 2 (concurrent safe)         │
│  │   │   └── ...                                                     │
│  │   └── .latest -> 002-user-profile  ← Symlink to most recent      │
│  └── .speckit-vc.json          ← Global config                       │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### Complete Workflow with Isolation

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SPECKIT VIBE CODING WORKFLOW                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [User Requirement]                                                  │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────────┐                                                 │
│  │ 1. AGENT Q&A    │ ◄── Agent (this skill) asks user directly      │
│  │    (In Chat)    │     User answers in conversation               │
│  └────────┬────────┘                                                 │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                 │
│  │ 2. GENERATE     │ ◄── Agent runs: init_spec.py --auto-dir        │
│  │    ISOLATED DIR │     Creates: specs/001-feature-name/           │
│  │    + SPEC FILE  │     Saves: requirements.json, SPECIFICATION.md │
│  └────────┬────────┘                                                 │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                 │
│  │ 3. AUTONOMOUS   │ ◄── vibe_workflow.py --spec-dir specs/001-...  │
│  │    WORKFLOW     │     All stages in same isolated directory      │
│  └────────┬────────┘     No conflicts with other features           │
│           │                                                          │
│  ┌────────┴────────────────────────────────────────────────────┐    │
│  │  specify → clarify → plan → tasks → checklist               │    │
│  │      → analyze → implement (parallel tasks)                  │    │
│  │                                                              │    │
│  │  All outputs in: specs/001-feature-name/                    │    │
│  └────────┬────────────────────────────────────────────────────┘    │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                 │
│  │ 4. LEARNING     │ ◄── Collect issues and update AGENTS.md        │
│  │    COLLECTION   │     At session end (not immediately)           │
│  └─────────────────┘                                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Create isolated directory and SPECIFICATION.md
python3 scripts/init_spec.py --from-json /tmp/requirements.json --auto-dir
# Output: specs/001-feature-name/

# Full autonomous workflow with isolated directory
python3 scripts/vibe_workflow.py --auto --spec-dir specs/001-feature-name

# Resume interrupted workflow
python3 scripts/vibe_workflow.py --resume

# Execute single task
python3 scripts/vibe_task.py --task T001 --spec-dir specs/001-feature-name

# List available agent adapters
python3 scripts/config-manager.py adapters
```

## Autonomous Mode Behavior

In `--auto` mode, the workflow operates fully autonomously with **no user interaction**:

| Stage | Autonomous Behavior |
|-------|---------------------|
| specify | Transforms SPECIFICATION.md into structured spec |
| clarify | AI identifies and resolves ambiguities automatically |
| plan | AI creates technical implementation plan |
| tasks | AI generates phased task breakdown |
| checklist | AI generates quality checklists automatically |
| analyze | AI checks consistency across all artifacts |
| implement | AI executes ALL tasks in dependency order |

> **Note**: The `--interactive` mode has been deprecated. Requirements gathering should be done by the Agent directly in conversation with the user, then `--auto` mode should be used for execution.

## Configuration

Configure via `.speckit-vc.json` in project root:

```json
{
  "agent": "copilot",
  "log_level": "INFO",
  "max_parallel": 3,
  "auto_learning": true,
  "timeout_minutes": 30,
  "session_isolation": true,
  "spec_vibes_dir": "spec-vibes"
}
```

See [📋 Configuration Reference](references/config-reference.md) for all options.

## Workflow Stages

Each stage runs in an **isolated session** to prevent context explosion:

| Stage | Agent | Input | Output |
|-------|-------|-------|--------|
| specify | speckit.specify | SPECIFICATION.md | spec.md |
| clarify | speckit.clarify | spec.md | clarified spec.md |
| plan | speckit.plan | spec.md | plan.md |
| tasks | speckit.tasks | plan.md, spec.md | tasks.md |
| checklist | speckit.checklist | tasks.md | checklists/*.md |
| analyze | speckit.analyze | all artifacts | analysis report |
| implement | speckit.implement | tasks.md | code |

See [🔄 Workflow Stages](references/workflow-stages.md) for detailed stage documentation.

## Vibe Session Directory Structure

Each vibe session creates an isolated directory under `spec-vibes/`:

```
spec-vibes/
├── 001-user-auth/                      # First feature
│   ├── SPECIFICATION.md                # Requirements specification
│   ├── spec.md                         # Generated spec
│   ├── plan.md                         # Technical plan
│   ├── tasks.md                        # Task list
│   ├── checklists/                     # Quality checklists
│   ├── sessions/                       # Session logs
│   └── copilot-logs/                   # Detailed debug logs
└── 002-oauth2/                         # Second feature
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Stages being skipped | Use `--auto --no-ask-user` together |
| Workflow stopped early | Add `--no-ask-user` for full autonomous execution |
| Context explosion | Ensure `session_isolation: true` in config |
| Tasks not parallel | Only tasks marked `[P]` run concurrently |
| Learnings not in AGENTS.md | Run `learning-collector.py --update-agents` |

---

## References

Load references based on your scenario:

| Reference | When to Load |
|-----------|--------------|
| [📋 Configuration Reference](references/config-reference.md) | Configuring settings, understanding options |
| [🔄 Workflow Stages](references/workflow-stages.md) | Understanding stage details, debugging stages |
| [📝 Task Format](references/task-format.md) | Creating/editing tasks, understanding markers |
| [🔧 Adapter Guide](references/adapter-guide.md) | **Development**: Creating new agent adapters |
| [📜 Scripts Reference](references/scripts-reference.md) | **Development**: Script options and internals |
| [🛠️ Development Guide](references/development-guide.md) | **Development**: Modifying speckit-vibe itself |
