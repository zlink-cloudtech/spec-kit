# 6. Standalone Documentation Management Agent

**Date**: 2026-03-13
**Status**: Accepted

## Context

The Spec-Driven Development lifecycle includes a dedicated `speckit-librarian` skill that handles documentation convergence at the end of a feature branch (the `converge` phase). This skill is phase-bound — it is activated via `check-prerequisites.sh`, which requires an active feature branch.

Teams frequently need to perform targeted documentation updates outside the SDD feature lifecycle: refreshing an outdated guide, adding a new ADR for a retroactive decision, renaming a file after a restructuring, or merging redundant documents. These operations are point-in-time utility tasks, not lifecycle phases.

Two implementation options were evaluated: (1) extend `speckit-librarian` with an additional mode, or (2) create a new, independent command template and skill.

Extending `speckit-librarian` would couple a lifecycle-independent utility to the converge phase lifecycle hook. The `check-prerequisites.sh` infrastructure requires an active feature branch; doc-update must work without one. Mixing lifecycle-bound and lifecycle-free responsibilities in one skill violates the Single Responsibility Principle and the Multi-Agent Portability principle (Constitution Principle V).

A dedicated `speckit-doc-updater` skill registered under a custom `doc-update` phase hook can be invoked standalone via `resolve-skills.py doc-update .` — no feature branch required. The command template (`templates/commands/doc-update.md`) is auto-distributed to all agents by the existing `generate_commands()` function in `create-release-packages.sh`, requiring no changes to the release packaging infrastructure.

## Decision

**Create a new, lifecycle-independent `/speckit.doc-update` command and a dedicated `speckit-doc-updater` skill rather than extending `speckit-librarian`.**

The new skill (`skills/speckit-doc-updater/`) is registered under a custom `doc-update` phase hook in `speckit-adapter.yaml`. The command template (`templates/commands/doc-update.md`) does not call `check-prerequisites.sh` and does not require an active feature branch. The skill supports six documentation operations: update content, add, delete, deprecate, rename/move, merge, and reposition — each synchronized to `memory/system-map.md` after execution.

A hard-stop rule is enforced: if `memory/system-map.md` does not exist, the agent reports the missing file and instructs the user to run `/speckit.constitution`. No auto-creation of the system map occurs.

Cross-reference scanning for rename/move/merge operations is deliberately scoped to files listed in `memory/system-map.md` plus the project root `README.md`. This bound is safe and predictable for systems with 1–500 tracked documents, and avoids unintended side-effects on untracked files.

Partial failure handling follows an auditable report-only protocol: the agent lists completed steps, identifies the failed step with its reason, and provides a manual recovery command. No automated rollback is attempted, as it risks compounding the original error.

## Consequences

**Positive**:

- `/speckit.doc-update` is invocable at any time without an active feature branch, making it a true utility command.
- `speckit-librarian` remains focused on lifecycle-bound convergence tasks; its responsibilities do not expand.
- Auto-distribution via `generate_commands()` requires zero changes to release packaging.
- The `doc-update` phase hook is independently testable via `python3 scripts/resolve-skills.py doc-update .`.
- Partial failure reporting provides auditability without automated rollback risk.
- The hard-stop on missing `memory/system-map.md` prevents silent data loss against an uninitialized project.

**Negative / Trade-offs**:

- A separate skill file must be maintained; over time, `speckit-librarian` and `speckit-doc-updater` may need to stay in sync as shared documentation concepts evolve.
- Users must explicitly invoke `/speckit.doc-update`; there is no automatic trigger — this is intentional (the operation is always user-initiated).
- Cross-reference scanning limited to tracked files and `README.md` may miss references in untracked Markdown files; users must update those manually.
