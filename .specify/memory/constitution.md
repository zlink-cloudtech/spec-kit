<!--
## Sync Impact Report

**Version Change**: (template) → 1.0.0
**Modified Principles**: N/A (initial fill — all principles newly defined)
**Added Sections**: Core Principles (I–V), Development Workflow, Quality Standards, Governance
**Removed Sections**: None (template placeholders replaced)

**Templates Requiring Updates**:
- `.specify/templates/plan-template.md` ✅ — Constitution Check gate present; compatible
- `.specify/templates/spec-template.md` ✅ — No constitution-specific references; compatible
- `.specify/templates/tasks-template.md` ✅ — References "Article IV (Test-First Imperative)" — aligns with Principle IV defined here
- `.specify/templates/commands/` ✅ — No commands subdirectory present in `.specify/templates/`; N/A
- `README.md` ✅ — Consistent with constitution principles
- `docs/quickstart.md` ✅ — Consistent with SDD lifecycle described in Principle III

**Deferred TODOs**: None — all placeholders resolved from repo context.
-->

# Spec Kit Constitution

## Core Principles

### I. Specification First

Specifications are the **primary artifact** of this project. Code serves specifications —
not the other way around. Every feature MUST begin with a written `spec.md` that captures
intent, user scenarios, and acceptance criteria before any implementation begins. Maintaining
software means evolving specifications first.

**Non-negotiable rules**:
- No implementation task may begin without an approved `spec.md`.
- All design decisions, ADRs, and plans MUST trace back to a specification.
- Specifications are versioned in branches and merged like code.
- Branch names MUST follow the `type/###-name` format (e.g., `feat/001-user-auth`).

### II. Executable Specifications

Specifications MUST be precise, complete, and unambiguous enough to drive implementation
plans and code generation. Ambiguity is a defect. The gap between intent and implementation
is eliminated by design, not by heroic effort.

**Non-negotiable rules**:
- Each user story MUST include independently testable acceptance scenarios.
- Plans (`plan.md`) MUST include a Constitution Check gate before implementation begins.
- Specifications that cannot produce a viable implementation plan are considered incomplete.
- Spec directories MUST use the flat `###-name` format under `specs/` (no type prefix).

### III. Lifecycle Integrity

The 6-phase SDD lifecycle (Specify → Clarify → Plan → Task → Implement → Converge) MUST be
followed for all features. No phase may be skipped. The `<!-- CONVERGENCE_BOUNDARY -->` marker
MUST be present in every `tasks.md`, separating implementation tasks from documentation
convergence tasks.

**Non-negotiable rules**:
- `/speckit.implement` enforces a hard stop at `CONVERGENCE_BOUNDARY`.
- Phase N (Converge) runs exclusively via `/speckit.converge`.
- The system map (`.specify/memory/system-map.md`) and ADRs MUST be updated during Converge.
- Significant architectural decisions MUST be recorded as ADRs in `docs/adr/`.

### IV. Test-First Imperative (NON-NEGOTIABLE)

Test-Driven Development is MANDATORY. Tests MUST be written and approved before
implementation code is written. The Red-Green-Refactor cycle is strictly enforced for
all new features and bug fixes.

**Non-negotiable rules**:
- Tests MUST be written before implementation: red → green → refactor.
- No PR may be merged with failing tests or without coverage for new functionality.
- Integration tests MUST cover: contract changes, inter-service communication, shared schemas.
- `pytest` is the standard test runner; `unittest.mock` (stdlib) for all mocking needs.

### V. Multi-Agent Portability

The toolkit MUST work equivalently across all supported AI agents. Agent-specific
conventions MUST be isolated to their configuration directories. Core templates and
scripts MUST remain agent-agnostic and portable.

**Non-negotiable rules**:
- Agent keys in `AGENT_CONFIG` MUST match the actual CLI executable name exactly
  (e.g., `cursor-agent`, not `cursor`). This eliminates special-case mappings.
- Bash (`scripts/bash/`) and PowerShell (`scripts/powershell/`) scripts MUST be
  kept in sync — every feature MUST be implemented in both.
- Core template placeholders MUST use generic syntax; agent-specific argument formats
  (`$ARGUMENTS` vs `{{args}}`) belong only in agent-specific command files.

## Development Workflow

The SDD 6-phase lifecycle governs all development on this project:

| Phase      | Command               | Description                                                  |
|------------|-----------------------|--------------------------------------------------------------|
| Specify    | `/speckit.specify`    | Create feature specification from natural language           |
| Clarify    | `/speckit.clarify`    | De-risk ambiguities (optional)                               |
| Plan       | `/speckit.plan`       | Design architecture, ADRs, data models, contracts            |
| Task       | `/speckit.tasks`      | Generate dependency-ordered tasks with CONVERGENCE_BOUNDARY  |
| Implement  | `/speckit.implement`  | Execute Phases 1 through N-1 (hard stop at boundary)         |
| Converge   | `/speckit.converge`   | Phase N — update docs, ADRs, system map, close gaps          |

**Version changes** to `src/specify_cli/__init__.py` MUST be accompanied by a version
increment in `pyproject.toml` and a corresponding entry in `CHANGELOG.md`.

## Quality Standards

- **Language**: All CLI source code targets Python 3.11+.
- **Linting**: `ruff check .` MUST pass before any PR is merged.
- **Testing**: All tests MUST pass. Run with `cd src && pytest`.
- **Skill-First Policy**: When a skill exists for a task, it MUST be used instead of
  ad-hoc implementation. Skill instructions override general training data.
- **Documentation**: ADRs MUST be recorded for all significant architectural decisions
  in `docs/adr/`. The system map MUST be kept current after every feature completion.

## Governance

This constitution supersedes all other development practices and guidelines for the
Spec Kit project. All contributors, reviewers, and AI agents operating on this project
MUST comply with these principles.

**Amendment Procedure**:
1. Propose the amendment within a spec or PR description.
2. Increment `CONSTITUTION_VERSION` following semantic versioning:
   MAJOR = incompatible principle removal/redefinition; MINOR = new principle/section;
   PATCH = clarifications or wording fixes.
3. Update `LAST_AMENDED_DATE` to the amendment date (ISO format YYYY-MM-DD).
4. Propagate changes to dependent templates (plan, spec, tasks) and the system map.
5. Record amendment in `CHANGELOG.md`.

**Compliance Review**: All PRs and agent-generated plans MUST include a Constitution Check
verifying alignment with the five principles above. Complexity MUST be justified against
Principle II (Executable Specifications). Use `AGENTS.md` and
`.github/instructions/specify-rules.instructions.md` for runtime development guidance.

**Version**: 1.0.0 | **Ratified**: 2026-03-03 | **Last Amended**: 2026-03-03
