---
description: Execute the System Convergence phase — update documentation, close gaps, and synchronize the system map.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__ converge
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__ -Phase converge
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. **Locate Convergence Tasks**: Read `tasks.md` and find the `<!-- CONVERGENCE_BOUNDARY -->` marker.
   - Extract all tasks **below** the boundary (Phase N: System Convergence).
   - If no boundary marker found, report error and suggest running `/speckit.tasks` to regenerate.

3. **Verify Pre-conditions**:
   - Check that all tasks **above** the boundary (Phases 1 through N-1) are marked as `[X]` (complete).
   - If incomplete tasks exist above the boundary, **STOP** and report:
     - List of incomplete tasks with their IDs
     - Prompt user: "Implementation tasks are not complete. Run `/speckit.implement` first."
   - If all pre-implementation tasks are complete, proceed.

4. **Load Convergence Context**:
   - **REQUIRED**: Read `plan.md` — extract "Documentation State Matrix" and "Gap Analysis" sections
   - **REQUIRED**: Read `memory/system-map.md` (if exists) — current documentation index
   - **IF EXISTS**: Read `memory/constitution.md` — governance principles
   - Load active skills for `converge` phase (speckit-librarian)

5. **Execute Phase N Tasks** in order:
   - For each task in the convergence phase:
     a. Read the task description and any `(Ref: ...)` context
     b. Execute the task following skill instructions
     c. Mark the task as `[X]` in tasks.md upon completion
   - **Task Categories**:
     - **ADR Tasks**: Create/update Architecture Decision Records in `docs/adr/`
     - **Documentation Tasks**: Update architecture docs, API docs, configuration guides
     - **System Map Tasks**: Synchronize `memory/system-map.md` with actual file state
     - **Gap Closure Tasks**: Create missing essential artifacts flagged in plan.md
     - **Validation Tasks**: Verify documentation completeness and TDD compliance

6. **Convergence Validation**:
   - Verify every entry in plan.md "Documentation State Matrix" has a completed task
   - Verify every entry in plan.md "Gap Analysis" has a completed bootstrapping task
   - Verify `memory/system-map.md` reflects the current state of all artifacts
   - Report any unclosed items as warnings

7. **Convergence Report**: Output summary including:
   - Documents updated (with paths)
   - ADRs created/updated
   - Gaps closed
   - System Map changes
   - Any remaining warnings or manual actions needed
   - Suggest running `/speckit.analyze` for final consistency check

## Key Rules

- Use absolute paths for all file operations
- Follow the speckit-librarian skill workflow strictly
- ADRs must use Michael Nygard format (Title, Status, Context, Decision, Consequences)
- System Map paths must be RELATIVE from repo root
- Do NOT modify implementation code — this phase is documentation-only
