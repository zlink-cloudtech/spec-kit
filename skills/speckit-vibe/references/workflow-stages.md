# Workflow Stages Reference

Detailed documentation for each stage in the speckit vibe coding workflow.

## Overview

The speckit-vibe workflow operates in a fully autonomous mode once requirements are gathered:

1. **Requirements Gathering** (Agent-driven, in conversation)
   - The Agent directly asks clarifying questions to the user
   - User answers in the chat conversation  
   - Agent generates SPECIFICATION.md

2. **Autonomous Execution** (No user interaction)
   - All stages run automatically without user prompts
   - AI makes reasonable assumptions and documents them

## Stage Overview

```
specify → clarify → plan → tasks → checklist → analyze → implement
```

| Stage | Purpose | Input | Output |
|-------|---------|-------|--------|
| specify | Convert requirements to spec | SPECIFICATION.md | spec.md |
| clarify | Refine and clarify spec | spec.md | updated spec.md |
| plan | Create technical plan | spec.md | plan.md |
| tasks | Generate task breakdown | plan.md, spec.md | tasks.md |
| checklist | Create quality checklists | tasks.md | checklists/*.md |
| analyze | Consistency analysis | all artifacts | analysis report |
| implement | Execute tasks | tasks.md | code |

## Stage 1: Specify

**Agent**: `/speckit.specify`

Transforms natural language requirements into a structured specification.

### Input
- SPECIFICATION.md or raw requirement text
- Available skills in `.github/skills/`

### Output
- `spec.md` in feature directory
- Branch created: `{number}-{short-name}`

### What It Does
1. Generates a concise short name for the feature
2. Creates a feature branch
3. Analyzes available skills for relevance
4. Generates spec.md with:
   - User stories
   - Functional requirements
   - Non-functional requirements
   - Success criteria
   - Skill alignment

### Example Command
```bash
copilot --model claude-sonnet-4.5 --allow-all --stream off \
  -p "/speckit.specify Add OAuth2 authentication with JWT tokens"
```

## Stage 2: Clarify

**Agent**: `/speckit.clarify`

Refines the specification by identifying and resolving ambiguities.

### Input
- spec.md from specify stage

### Output
- Updated spec.md with clarifications
- Clarification log

### What It Does
1. Identifies ambiguous or incomplete requirements
2. Generates clarifying questions
3. **In autonomous mode**: AI answers its own questions
4. Updates spec.md with clarified requirements

### Key Behaviors
- Maximum 3 `[NEEDS CLARIFICATION]` markers
- Prioritizes: scope > security > UX > technical details
- Makes informed guesses based on industry standards

## Stage 3: Plan

**Agent**: `/speckit.plan`

Creates a technical implementation plan.

### Input
- spec.md (clarified)

### Output
- plan.md with:
  - Tech stack selection
  - Architecture decisions
  - Project structure
  - Data model (if applicable)
  - API contracts (if applicable)

### What It Does
1. Analyzes requirements from spec.md
2. Selects appropriate technologies
3. Designs system architecture
4. Creates file structure
5. Defines data models and relationships

## Stage 4: Tasks

**Agent**: `/speckit.tasks`

Generates actionable, dependency-ordered tasks.

### Input
- plan.md
- spec.md
- Optional: data-model.md, contracts/, research.md

### Output
- tasks.md with:
  - Phase-organized tasks
  - Task IDs and dependencies
  - Parallel markers [P]
  - File paths for each task

### Task Format
```markdown
- [ ] T001 Create project structure per implementation plan
- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py
- [ ] T012 [P] [US1] Create User model in src/models/user.py
```

### Phase Structure
1. **Phase 1: Setup** - Project initialization
2. **Phase 2: Foundational** - Blocking prerequisites
3. **Phase 3+: User Stories** - One phase per story
4. **Final Phase: Polish** - Cross-cutting concerns

## Stage 5: Checklist

**Agent**: `/speckit.checklist`

Generates quality checklists for validation.

### Input
- tasks.md
- spec.md

### Output
- `checklists/*.md` files for different concerns:
  - requirements.md
  - ux.md (if applicable)
  - security.md (if applicable)
  - test.md (if applicable)

### What It Does
1. Identifies quality concerns from spec
2. Creates validation checklists
3. Maps checklist items to tasks
4. Ensures coverage of success criteria

## Stage 6: Analyze

**Agent**: `/speckit.analyze`

Performs consistency analysis across all artifacts.

### Input
- spec.md
- plan.md
- tasks.md
- checklists/

### Output
- Analysis report with:
  - Duplications detected
  - Ambiguities flagged
  - Coverage gaps
  - Consistency issues
  - Remediation suggestions

### What It Does
1. Builds semantic models of all artifacts
2. Detects duplications and inconsistencies
3. Validates skill alignment
4. Checks task coverage
5. Generates remediation plan

### Severity Levels
- **CRITICAL**: Blocks implementation, must fix
- **HIGH**: Should fix before implementation
- **MEDIUM**: Fix during implementation
- **LOW**: Nice to have

## Stage 7: Implement

**Agent**: `/speckit.implement`

Executes the implementation plan by processing tasks.

### Input
- tasks.md
- plan.md
- All supporting artifacts

### Output
- Working code
- Updated tasks.md (completed items marked)
- Session logs

### Execution Flow
1. Check checklists status
2. Load implementation context
3. Set up project structure
4. Execute tasks phase by phase
5. Validate completed work

### Parallel Execution
Tasks marked `[P]` execute concurrently up to `max_parallel`:

```bash
# Execute phase with parallelism
scripts/vibe-task.sh --phase 3 --parallel 3 --spec-dir .specify/specs/001-feature
```

### Self-Correction
If issues discovered during implementation:
1. Update tasks.md with new/modified tasks
2. Re-run analyze stage
3. Update dependent artifacts
4. Resume implementation

## Session Isolation

Each stage runs in an **isolated copilot session**:

```bash
copilot --model "$MODEL" $ALLOW_TOOLS --stream off -p "/speckit.$STAGE $ARGS"
```

### Benefits
- Prevents context explosion
- Clean state for each stage
- Easier debugging
- Reproducible execution

### State Persistence
State persisted via files, not session context:
- `.speckit-vc/state.json` - Workflow state
- `.speckit-vc/sessions/*.log` - Session logs
- `.speckit-vc/tasks/*.json` - Task status

## Resuming Workflows

### Resume from Specific Stage
```bash
scripts/vibe-workflow.sh --stage plan --spec-dir .specify/specs/001-feature
```

### Check Current State
```bash
scripts/state-tracker.py status
```

### Get Next Stage
```bash
scripts/state-tracker.py resume
```

## Error Recovery

### Stage Failure
```bash
# Check what failed
scripts/state-tracker.py status

# Retry from failed stage
scripts/vibe-workflow.sh --stage <failed-stage> --spec-dir <dir>
```

### Task Failure
```bash
# Check task status
scripts/state-tracker.py task status T005

# Retry specific task
scripts/vibe-task.sh --task T005 --spec-dir <dir>
```

## Re-analysis After Changes

When making manual changes to artifacts:

```bash
scripts/vibe-workflow.sh --reanalyze --spec-dir .specify/specs/001-feature
```

This runs the analyze stage and reports any new inconsistencies.
